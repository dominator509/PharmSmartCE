# Prompt: Debug a Failing Validation

Paste this prompt into a coding agent when a validation command is failing
inside an ExecPlan run.

---

You are a coding agent in the PharmSmartCE repository. A validation command
is failing:

- Failing command: **[FAILING_COMMAND]**
- Error excerpt: **[ERROR_EXCERPT]**
- Active ExecPlan: **[EXECPLAN_PATH]**

Procedure:

1. Read `AGENTS.md` — especially §7 (Anti-Fixation / Bounded Retry).
2. Do NOT rewrite unrelated code. Do NOT perform broad refactors. Do NOT
   change config that is not implicated by the error.
3. Capture, exactly, into the active ExecPlan's `Surprises & Discoveries`:
   - The failing command.
   - The first ~30 lines of the error.
   - The file/line(s) the traceback implicates.
4. Form **ONE** hypothesis for the root cause. Write it in
   `Surprises & Discoveries`.
5. Apply the **smallest targeted fix** consistent with that hypothesis.
6. Rerun ONLY the narrowest command that reproduces the failure (e.g.,
   `pytest tests/unit/test_X.py::TestY::test_z -x -vv`). Do not rerun the
   whole suite.
7. If the same root failure persists:
   - **2nd attempt:** create a narrower diagnostic (single-file repro;
     temporary scratch script outside `app/` is fine). Localize the cause.
   - **3rd attempt:** stop the current approach. Record failed hypotheses
     in `Surprises & Discoveries`. Choose a simpler implementation path
     (drop the dep, use a working pattern from elsewhere, fall back to
     sync). Continue if safe.
8. After fixing, rerun the original validation. If it passes, continue the
   ExecPlan; if it fails with a new root cause, repeat from step 4 with a
   fresh hypothesis count.
9. If still blocked AND no simpler path exists → STOP S5. Report per
   `AGENTS.md` §15 with S5 evidence and the smallest decision needed.

Forbidden:
- Patching around the same error without a new hypothesis.
- Lowering test assertions to make a test "pass".
- Removing a failing test instead of fixing the bug.
- Disabling `CitationValidator`, `InjectionDetector`, or the OpenAI cap to
  unblock.
