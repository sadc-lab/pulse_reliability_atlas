# Pulse Reliability Atlas -- convenience targets.
#
# The cross-platform entry point is scripts/verify.py, which runs everywhere
# including the Windows laptop (no `make` required there):
#
#     uv run python scripts/verify.py
#
# On systems with GNU make (CI / Linux / macOS) the targets below wrap it.

.PHONY: verify audit figures

## verify: full reproducibility gate -- regenerate figures -> build PDFs
##         (best-effort) -> run both claims-ledger audits. Non-zero on failure.
verify:
	uv run python scripts/verify.py

## audit: claims-ledger audits only (monograph ledger + paper crosswalk).
##        Each invocation exits non-zero on any FAIL.
audit:
	uv run python scripts/audit_claims.py
	uv run python scripts/audit_claims.py --check-paper-sync

## figures: regenerate every data-derived figure + the traffic-light artefacts.
figures:
	uv run python scripts/make_figures.py
	uv run python scripts/make_paper_fig03.py
	uv run python scripts/make_paper_fig04.py
	uv run python scripts/make_supp_fig_s1.py
	uv run python scripts/make_supp_fig_s3.py
	uv run python scripts/make_supp_fig_s4.py
	uv run python scripts/export_traffic_light.py
