# Atlas-only Pulse Engine container.
#
# Builds on the official Kitware Pulse 4.3.1 image (Apache-2.0). The atlas
# wrapper is a fork of Pulse_translation_new's run_validation_engine.py with
# FIO2_MAX raised to 1.0 so the preregistered Morris sweep
# (`preregistration.md` §Inputs, FiO2 ∈ [0.21, 1.0]) is never silently capped
# by the wrapper layer.
#
# Build:   docker build -t pulse-atlas-engine engine/
# Run:     docker run --rm -v /path/to/case_dir:/data pulse-atlas-engine

FROM kitware/pulse:4.3.1

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/pulse/python:/pulse/bin
ENV LD_LIBRARY_PATH=/pulse/bin

RUN python3 -m pip install --no-cache-dir pandas

COPY run_atlas_engine.py /app/run_atlas_engine.py

RUN mkdir -p /data /pulse/bin/out

WORKDIR /app

ENTRYPOINT ["python3", "run_atlas_engine.py"]
CMD ["--config", "/data/config.json", "--output", "/data/output.csv"]
