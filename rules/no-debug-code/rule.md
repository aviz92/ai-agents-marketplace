# No Debug Code

Do not leave debug artifacts in source files.

**Forbidden in production code:**
- `print(...)` statements (use structured logging instead)
- `breakpoint()` calls
- `import pdb` / `pdb.set_trace()`
- `import ipdb` / `ipdb.set_trace()`
- `assert` statements used for runtime validation (use explicit `if`/`raise`)

If you spot any of these while working in a file, remove them or replace with the
appropriate `logging` call before completing the task.
