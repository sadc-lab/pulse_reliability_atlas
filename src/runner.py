"""Docker runner for the atlas Pulse engine.

Each call to `run_one(...)` materializes a config under
``data/runs/<case_id>/`` and invokes ``pulse-atlas-engine`` against it.
Output is written into the same directory:

    data/runs/<case_id>/
        config.json
        output.csv
        output_pulse_native.csv
        pulse.log               (combined stdout+stderr from the container)
        run_meta.json           (exit code, wall time, image, command)

`run_many(...)` parallelises calls with a `ThreadPoolExecutor`, defaulting to
3 workers — verified safe on the maintainer's machine
(`experiments_log/santino/S001_docker_smoke_test.md`). Do NOT raise above 3
on the i5-11400H / 8 GB / 3.95 GB Docker allocation; the cap is a hardware
budget, not a parallelism preference.
"""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


DEFAULT_IMAGE: str = "pulse-atlas-engine"
# Lowered from 3 → 2 mid-sweep (S006) on user's request to reduce thermal load
# on the laptop during the long overnight run. Sweep was resumed via --resume
# without losing any completed runs.
MAX_PARALLEL_LAPTOP: int = 2  # do not raise without re-verifying RAM headroom

# Per-container resource caps — preserved from the verified template
# (`reference/pulse_run_template.md`).
DOCKER_MEMORY: str = "1g"
DOCKER_CPUS: str = "3"


@dataclass
class RunResult:
    """Outcome of one Pulse run."""

    case_id: str
    run_dir: Path
    config_path: Path
    csv_path: Path | None
    log_path: Path
    exit_code: int
    wall_time_s: float
    image: str

    def to_meta_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "run_dir": str(self.run_dir),
            "config_path": str(self.config_path),
            "csv_path": str(self.csv_path) if self.csv_path else None,
            "log_path": str(self.log_path),
            "exit_code": self.exit_code,
            "wall_time_s": self.wall_time_s,
            "image": self.image,
        }


def _host_path_for_volume(p: Path) -> str:
    """Return the path string Docker expects for a -v bind mount.

    On Git Bash / MSYS, paths like ``C:/...`` need to be expressed with a
    leading drive letter and forward slashes. We use ``platform.system()``
    rather than checking shell flags because this code may be invoked from
    plain Python in the same shell.
    """
    resolved = str(Path(p).resolve())
    # Convert backslashes to forward slashes so Docker is happy on Windows.
    return resolved.replace("\\", "/")


def _build_docker_command(host_run_dir: Path, image: str) -> list[str]:
    host = _host_path_for_volume(host_run_dir)
    # Docker on Windows + MSYS needs the //data/... double-slash form.
    container_data = "//data" if platform.system() == "Windows" else "/data"
    config_in = f"{container_data}/config.json"
    output_in = f"{container_data}/output.csv"
    return [
        "docker", "run", "--rm",
        f"--memory={DOCKER_MEMORY}", f"--cpus={DOCKER_CPUS}",
        "-v", f"{host}:/data",
        image,
        "--config", config_in,
        "--output", output_in,
    ]


def run_one(
    config: dict[str, Any],
    case_id: str,
    runs_root: Path | str,
    image: str = DEFAULT_IMAGE,
    timeout_s: float = 600.0,
    overwrite: bool = False,
) -> RunResult:
    """Execute one Pulse run.

    Always returns a `RunResult`; non-zero exit codes / timeouts are reported
    via ``exit_code`` rather than raised. The caller (typically
    `aggregator.classify_run`) interprets the result with `src.detector`.
    """
    runs_root = Path(runs_root)
    run_dir = runs_root / case_id
    if run_dir.exists() and overwrite:
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)

    config_path = run_dir / "config.json"
    csv_path = run_dir / "output.csv"
    log_path = run_dir / "pulse.log"
    meta_path = run_dir / "run_meta.json"

    config_path.write_text(json.dumps(config, indent=2))

    cmd = _build_docker_command(run_dir, image)
    env = {**os.environ, "MSYS_NO_PATHCONV": "1"}  # idempotent on non-MSYS shells

    start = time.monotonic()
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_s,
            env=env,
        )
        exit_code = proc.returncode
        log_path.write_text((proc.stdout or "") + "\n--- STDERR ---\n" + (proc.stderr or ""))
    except subprocess.TimeoutExpired as e:
        exit_code = 124  # conventional "timeout"
        partial = ""
        if e.stdout:
            partial += e.stdout if isinstance(e.stdout, str) else e.stdout.decode("utf-8", "replace")
        partial += "\n--- TIMEOUT ---\n"
        if e.stderr:
            partial += e.stderr if isinstance(e.stderr, str) else e.stderr.decode("utf-8", "replace")
        log_path.write_text(partial)
    wall_time = time.monotonic() - start

    result = RunResult(
        case_id=case_id,
        run_dir=run_dir,
        config_path=config_path,
        csv_path=csv_path if csv_path.exists() else None,
        log_path=log_path,
        exit_code=exit_code,
        wall_time_s=wall_time,
        image=image,
    )
    meta_path.write_text(json.dumps(result.to_meta_dict(), indent=2))
    return result


def run_many(
    jobs: Iterable[tuple[dict[str, Any], str]],
    runs_root: Path | str,
    image: str = DEFAULT_IMAGE,
    max_workers: int = MAX_PARALLEL_LAPTOP,
    timeout_s: float = 600.0,
    overwrite: bool = False,
    progress: bool = True,
) -> list[RunResult]:
    """Run multiple jobs in parallel.

    `jobs` is an iterable of ``(config_dict, case_id)`` tuples.

    Returns the `RunResult`s in completion order (not submission order).
    Order is irrelevant for analysis since each run is independent and
    identified by its `case_id`.
    """
    if max_workers > MAX_PARALLEL_LAPTOP:
        raise ValueError(
            f"max_workers={max_workers} > {MAX_PARALLEL_LAPTOP}; "
            "raising would break the verified RAM/CPU budget."
        )

    results: list[RunResult] = []
    job_list = list(jobs)
    n = len(job_list)
    if progress:
        print(f"[runner] launching {n} job(s) on {max_workers} workers, image={image}")

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {
            ex.submit(run_one, cfg, cid, runs_root, image, timeout_s, overwrite): cid
            for cfg, cid in job_list
        }
        for i, fut in enumerate(as_completed(futures), 1):
            res = fut.result()
            results.append(res)
            if progress:
                tag = "OK " if res.exit_code == 0 else f"FAIL({res.exit_code})"
                print(
                    f"[runner] {i}/{n} {tag} {res.case_id} "
                    f"({res.wall_time_s:.1f}s)"
                )
    return results


__all__ = [
    "DEFAULT_IMAGE",
    "DOCKER_CPUS",
    "DOCKER_MEMORY",
    "MAX_PARALLEL_LAPTOP",
    "RunResult",
    "run_many",
    "run_one",
]
