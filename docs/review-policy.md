# Review and Docs Policy

This project treats documentation and reviews as part of the production delivery process.

## Required Review Inputs

- Clear summary of intent in PR description.
- Test plan with executed verification steps.
- Notes about operational impact and rollout.

## Repository Review Guardrails

- `CODEOWNERS` defines default reviewer ownership.
- `PULL_REQUEST_TEMPLATE` standardizes high-signal review context.

## Documentation Expectations

- Update docs whenever setup behavior, defaults, or workflow changes.
- Keep architecture and configuration references current.
- Prefer small, explicit doc updates in the same branch as code changes.

## Suggested Future Enforcement

- Branch protection requiring at least one approved review.
- CI checks for docs linting and link validation.
- Optional policy checks to ensure PR template sections are completed.
