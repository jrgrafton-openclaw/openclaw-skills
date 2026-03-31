# Coding-agent guidance

## Delegate safely

Give every coding agent task:
- current state / what is already done
- exact file paths
- acceptance criteria
- verification commands
- constraints (deps, style, no browser, etc.)

## Verification rule

Never trust a coding agent self-report for:
- deploy state
- browser behavior
- CI status
- pushed commits

Check the result directly before reporting to the user.
