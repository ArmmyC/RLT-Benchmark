# Bugfix Spec: Make Clean Portable on Windows

## Goal

Make the repository clean flow work on Windows environments where GNU `rm` is not available.

A clean full evidence validation reported:

```text
make clean failed because Make tried to invoke rm, which is not available in this Windows environment.
```

The user had to manually remove generated outputs with PowerShell before continuing. This is a local UX and reproducibility bug.

## Required behavior

`make clean` should work from the same Windows shell used for the rest of the Python-based flow, without requiring GNU `rm`.

The clean target should remove generated outputs safely and consistently on Windows, Linux, and macOS.

## Required changes

1. Add a Python clean helper, for example:

```text
python/tinysnnrfid/clean_outputs.py
python/clean_outputs.py
```

2. Update `Makefile` so `clean` calls the Python helper instead of direct `rm` commands.
3. The helper should remove generated outputs only, including at least:

```text
results/
__pycache__/
.pytest_cache/
*.pyc under project Python paths
```

4. Do not remove source files, configs, docs, tests, RTL source, or committed specs/prompts.
5. Make missing files/directories non-errors.
6. Print a concise summary of what was removed or skipped.
7. Keep existing evidence targets unchanged.
8. Update README if it currently documents `make clean` behavior.

## Tests

Add tests that do not rely on platform-specific shell commands:

1. The clean helper removes generated result files/directories.
2. The clean helper ignores missing paths.
3. The clean helper does not remove source/docs/config/test files.
4. The Makefile clean target calls the Python helper and does not directly invoke `rm`.
5. Existing tests continue to pass.

## Manual validation

Run:

```bash
python -m pytest
make clean
make rtl-doctor
```

On Windows, `make clean` must not fail due to missing `rm`.

## Constraints

- Do not add dependencies.
- Do not change benchmark, classifier, RTL, or evidence semantics.
- Do not remove generated-output policy.
- Do not commit generated outputs.

## Definition of done

- `make clean` is portable across Windows/Linux/macOS.
- Missing outputs do not cause failures.
- Tests cover clean safety and Makefile integration.
