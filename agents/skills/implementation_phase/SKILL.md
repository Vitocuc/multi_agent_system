# Phase 2: TDD Implementation Directives

1. Read the architectural boundaries in `specs/architecture_blueprint.md`.
2. Read the testing criteria in `specs/test_specification.md`.
3. Generate the required pytest suite in the `tests/` directory.
4. Implement the modular application code in the `core/` directory.
5. Execute the tests by running: `docker run --rm -v $(pwd):/workspace payment-team-image pytest`
6. If the tests fail, analyze the logs, patch the code, and re-run the container until all tests pass.
7. Conduct a final security audit on the multi-file structure to ensure no data leakage or idempotency flaws exist.