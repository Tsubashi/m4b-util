## Repository overview

- **Source code**: `src/m4b_util/` contains the application It is divided into Code used directly by a subcommand is in the `subcommands` folder, while shared code is in the `helpers` folder
- **Tests**: `tests/` .

## Local workflow

Lint and test your changes:

   ```bash
   flake8
   pytest
   ```

   To run a single test, use `pytest -s -k <test_name>`.

## Style notes

- Write comments as full sentences and end them with a period.

## Pull request expectations

PRs should provide a summary, test plan and issue number if applicable, then check that:

- New tests are added when needed.
- Documentation is updated.
- `flake8` and `pytest` have been run.
- The full test suite passes.

Commit messages should be a continuation of the phrase concise and written in the imperative mood. Small, focused commits are preferred.

## What reviewers look for

- Tests covering new behaviour.
- Consistent style: code formatted well, imports sorted, and linted with `flake8`.
- Clear documentation for any public API changes.
- Clean history and a helpful PR description.
