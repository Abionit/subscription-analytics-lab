# Contributing

This repository uses short-lived branches, focused commits, automated validation, and pull requests to keep changes traceable and reviewable.

## Branches

Create branches from the latest `main` using one of these prefixes:

- `feature/` for new capabilities
- `fix/` for defect corrections
- `docs/` for documentation changes
- `test/` for test coverage
- `chore/` for maintenance and tooling

Use a concise branch name such as `feature/add-daily-quality-metrics`.

## Commits

Write commit messages as `type: concise description`.

Accepted types include:

- `feat`: user-facing or pipeline capability
- `fix`: behavior correction
- `docs`: documentation only
- `test`: test additions or corrections
- `ci`: automation and workflow changes
- `refactor`: internal restructuring without behavior changes
- `chore`: maintenance work

Keep each commit focused on one logical change. Do not commit credentials, local environments, generated databases, or raw data exports.

## Local Validation

Run the checks relevant to the change before opening a pull request:

```bash
pip install -r requirements.txt
python -m compileall -q src scripts aws/glue tests
python -m unittest discover -s tests -v
cfn-lint infrastructure/cloudformation.yaml
```

Run the complete local pipeline when transformation logic, quality rules, or analytical outputs change:

```bash
python src/run_pipeline.py
```

## Pull Requests

A pull request should explain:

- the business or technical problem
- the implemented change
- the validation performed
- any impact on schemas, data quality, infrastructure, security, or cost

Keep pull requests small enough to review as one unit. Resolve automated checks and review comments before merging. Use squash merge so `main` preserves a concise, meaningful history.

## Data And Security

- Use synthetic or approved public data only.
- Store secrets in environment variables or a managed secret store.
- Review IAM permissions using least privilege.
- Document new AWS resources and expected cost implications.
- Add or update quality checks when introducing a source, field, or transformation.
