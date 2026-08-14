# Canonical Rebuild Sequence

## 1. Intake

Record the supplier, transfer method, date, archive name, and archive SHA-256. Do not execute anything until the published and calculated hashes match.

## 2. Clean environment

Use a new VM, container, or Python virtual environment. Record OS, architecture, Python, pip, locale, time zone, network state, and environment variables.

## 3. Verify the freeze

```bash
python 03_REBUILD_TOOLS/check_required_files.py --root .
python 03_REBUILD_TOOLS/verify_manifest.py --root . --manifest runtime_manifest.json
python 03_REBUILD_TOOLS/check_config_schema.py --root .
```

## 4. Install dependencies

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install --require-hashes -r requirements.lock
```

An unhashed or incomplete lockfile means `PARTIAL — DEPENDENCY FREEZE NOT VERIFIED`.

## 5. Run the frozen preflight

Use the exact command in the frozen reproducibility README. Preserve stdout, stderr, exit code, elapsed time, and output SHA-256. Do not patch the code.

## 6. Verify transport integrity

For every case confirm:

- all local residuals are finite;
- every residual is at or below the frozen tolerance;
- `G(M0) == G(M0_hat)`;
- divergence halts closed;
- NaN and infinity halt closed;
- simulated mode blocks operations and external claims.

## 7. Repeat three times

Compare outputs with `compare_rebuild_outputs.py`.

## 8. Report

Complete the rebuild report, deviation log, custody log, and independence declaration. A failed rebuild remains a failed rebuild under V11.4.
