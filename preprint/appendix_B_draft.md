# Appendix B — Adult Pulse Operational Envelope: Pre-Atlas Boundary Characterization

**B.1 Provenance and Methodology**
The boundary characterization, acceptance gates, and condition calibrations detailed in this appendix were established in companion developmental work prior to the execution of the preregistered Morris elementary effects sweep. They are documented here to define the exact adult operational envelope of the Pulse Physiology Engine (v4.3.1) and to ensure reproducibility. The complete experimental logs and Docker replication scripts for these boundary probes are available in the companion repository [Insert Citation/DOI].

**B.2 Hard Input Acceptance Gates**
Pulse 4.3.1 enforces strict patient initialization boundaries. Configurations outside these ranges result in immediate engine initialization failure prior to stabilization.
* **Heart Rate (HR):** The accepted baseline range is strictly 50–110 bpm. Probes confirmed rejection at 49 bpm and 111 bpm.
* **Respiratory Rate (RR):** The accepted baseline range is strictly 8–20 bpm. Probes confirmed rejection at 7 bpm and 21 bpm.
* **Blood Pressure (BP):** Systolic Blood Pressure (SBP) is constrained to 90–120 mmHg. Diastolic Blood Pressure (DBP) is constrained to 60–80 mmHg.
* **Pulse Pressure Constraint:** An undocumented constraint was identified during boundary probing: the engine requires a pulse pressure ratio where DBP / SBP <= 0.75. If this ratio is exceeded (e.g., SBP = 90 mmHg and DBP = 68 mmHg, ratio = 0.756), the initialization is rejected even if individual values fall within the allowed absolute ranges.
* **Fraction of Inspired Oxygen (FiO2):** Direct probing confirmed that the engine remains fully stable up to FiO2 = 1.0. The partial pressure of oxygen (PaO2) scales linearly by approximately 7.8 mmHg per 0.01 increase in FiO2.

**B.3 ARDS Severity Calibration and Solver Instability**
The Acute Respiratory Distress Syndrome (ARDS) condition in Pulse is modulated by an impairment fraction (0.0 to 1.0). To align with the Berlin Definition severity bands via PaO2/FiO2 (P/F) ratios, the fractions were empirically calibrated as follows:
* **Mild ARDS (P/F 200–300):** Impairment fraction = 0.26 (yields P/F ~ 256)
* **Moderate ARDS (P/F 100–200):** Impairment fraction = 0.60 (yields P/F ~ 148)
* **Severe ARDS (P/F < 100):** Impairment fraction = 0.95 (yields P/F ~ 75)

*Solver Instability Zone:* High-resolution fractional sweeps identified a numerical bifurcation in the respiratory solver. Impairment fractions between **0.91 and 0.945 (inclusive)** consistently result in fatal solver divergence. The calibrated severe fraction (0.95) was selected to safely clear this instability zone.

**B.4 Source-Code Audit Findings and Discrepancies**
A source-level audit of the Pulse 4.3.1 C++ repository identified three discrepancies between the official methodology documentation and the compiled engine logic:
1. **Basal Metabolic Rate (BMR) Coefficient:** The documentation lists the male weight coefficient as 3.397. The codebase implements `13.397` (`SetupPatient.cpp:771`), correctly aligning with the Harris-Benedict equation (Roza & Shizgal 1984).
2. **Skin Surface Area Exponent:** The documentation lists the weight exponent as 0.45. The codebase implements `0.425` (`SetupPatient.cpp:752`), aligning with the Du Bois formula.
3. **Baroreceptor Constant (v):** The documentation lists the baroreceptor exponent as 4. The codebase implements an effective v = 48 (`NervousModel.cpp:320`), calculated as `4 * ResponseSlope` (where slope = 12).
