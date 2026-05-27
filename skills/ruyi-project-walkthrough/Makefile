.PHONY: test check generate verify ci release clean

test:
	python -m pytest tests/ -v --tb=short

test-quick:
	python -m pytest tests/ -q --tb=line

check:
	./scripts/convert.sh --check

generate:
	./scripts/convert.sh

verify:
	python scripts/verify_sources.py --check-all examples/ --strict

ci: test check
	@echo "CI checks passed."

release:
	@./scripts/release.sh $(VERSION)

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	rm -f .coverage

help:
	@echo "Targets:"
	@echo "  test       Run full test suite with verbose output"
	@echo "  test-quick Run tests in quiet mode"
	@echo "  check      Verify platform files are in sync"
	@echo "  generate   Regenerate all platform files from SKILL.md"
	@echo "  verify     Run manifest verification on examples"
	@echo "  ci         Run all CI checks (test + check)"
	@echo "  release    Run release workflow (VERSION=x.y.z)"
	@echo "  clean      Remove cache files"
