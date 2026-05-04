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

# Patch upstream Pulse 4.3.1 Python SDK bug: serialize_mechanical_ventilator_*_to_bind
# writes patient-trigger fields to dst.InspirationCycle{Flow,Pressure}, but the
# protobuf field names are dst.InspirationPatientTrigger{Flow,Pressure}. Result:
# AttributeError on any VC-AC / PC-AC / CPAP action that sets a patient trigger.
# Verified against MechanicalVentilatorActions.proto. Only Inspiration* is
# affected; Expiration*Cycle{Flow,Pressure} are real fields and untouched.
# See experiments_log/santino/S014_trigger_pressure_lockout.md for diagnosis.
RUN sed -i \
    -e 's/dst\.InspirationCycleFlow/dst.InspirationPatientTriggerFlow/g' \
    -e 's/dst\.InspirationCyclePressure/dst.InspirationPatientTriggerPressure/g' \
    /pulse/python/pulse/cdm/io/mechanical_ventilator_actions.py

COPY run_atlas_engine.py /app/run_atlas_engine.py

RUN mkdir -p /data /pulse/bin/out

WORKDIR /app

ENTRYPOINT ["python3", "run_atlas_engine.py"]
CMD ["--config", "/data/config.json", "--output", "/data/output.csv"]
