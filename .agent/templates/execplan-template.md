# EP-NNN — <Title>

**Phase:** P<X>

## 1. Purpose / Big Picture
(One paragraph: why this plan exists; the user-visible outcome it produces.)

## 2. Scope
- (Bullet things this plan WILL do.)

## 3. Non-goals
- (Bullet things this plan WILL NOT do.)

## 4. Context and Orientation
(Where this lands in the system. Link to ARCHITECTURE map sections and
relevant specs.)

## 5. Files to Read First
- `(path)`
- `(path)`

## 6. Files to Change
- `(path)`
- `(path)`

## 7. Interfaces and Contracts
(APIs, schemas, types, adapter Protocols affected.)

## 8. Milestones

### M1: <goal>
- **Files to read:** `(paths)`
- **Files to change:** `(paths)`
- **Exact edits expected:** (one line per file)
- **Validation command:** `(exact command from COMMANDS.md)`
- **Expected result:** (string, exit code, or test name)
- **Recovery:** (bounded-retry guidance per AGENTS §7)

### M2: <goal>
(repeat)

## 9. Concrete Steps
Execute milestones in order. After each: run validation, verify expected,
tick `Progress`, append one-line note. Apply bounded-retry on any failure.
Continue autonomously. Stop only under STOP conditions.

## 10. Validation and Acceptance
- All milestone validations pass.
- `scripts/verify.sh` exit 0.
- Acceptance criteria:
  - [ ] (criterion 1)
  - [ ] (criterion 2)

## 11. Idempotence and Recovery
(How re-running is safe. Migration ids; idempotency keys; etc.)

## 12. Progress
- [ ] M1: <goal>
- [ ] M2: <goal>

## 13. Surprises & Discoveries
(empty — append entries here as they occur)

## 14. Decision Log
(empty — append entries here as they occur)

## 15. Outcomes & Retrospective
(to be filled at completion)
