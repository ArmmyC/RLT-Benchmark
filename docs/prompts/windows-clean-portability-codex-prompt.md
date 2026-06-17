# Codex Prompt: Make Clean Portable on Windows

Implement:

```text
docs/specs/windows-clean-portability.md
```

Goal: make `make clean` work on Windows environments where GNU `rm` is not available.

Context:
A clean full evidence validation failed because the Makefile tried to invoke `rm`, which was missing in the Windows shell. The user had to manually remove generated outputs with PowerShell before continuing.

Required:
1. Add a Python clean helper, for example:
   - `python/tinysnnrfid/clean_outputs.py`
   - wrapper `python/clean_outputs.py`
2. Update `Makefile` so `clean` calls the Python helper instead of direct `rm` commands.
3. Remove generated outputs only, including at least:
   - `results/`
   - `__pycache__/`
   - `.pytest_cache/`
   - `*.pyc` under project Python paths
4. Do not remove source files, configs, docs, tests, RTL source, or committed specs/prompts.
5. Missing files/directories should not be errors.
6. Print a concise summary of what was removed or skipped.
7. Keep evidence targets unchanged.
8. Update README if needed.

Add tests:
- clean helper removes generated result files/directories
- clean helper ignores missing paths
- clean helper does not remove source/docs/config/test files
- Makefile clean target calls the Python helper and does not directly invoke `rm`
- existing tests continue to pass

Run:
```bash
python -m pytest
make clean
make rtl-doctor
```

Final response:
Summarize changed files, tests run, and confirm `make clean` no longer depends on GNU `rm`.

Constraints:
- Do not add dependencies.
- Do not change benchmark, classifier, RTL, or evidence semantics.
- Do not commit generated outputs.
