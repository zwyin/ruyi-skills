.PHONY: test ci release convert clean check test-collection

SKILLS := $(shell ls -d skills/*/)

test:
	@for skill in $(SKILLS); do \
		if [ -f "$$skill/tests/conftest.py" ] || [ -f "$$skill/requirements-dev.txt" ]; then \
			echo "=== Testing $$skill ==="; \
			cd "$$skill" && python3 -m pytest tests/ -q --tb=short 2>&1; \
			cd - > /dev/null; \
		fi; \
	done

ci: test check test-collection
	@echo "=== All checks passed ==="

check:
	@echo "Checking marketplace.json..."
	@python3 -c "import json; json.load(open('.claude-plugin/marketplace.json'))"
	@echo "Checking skill self-containment..."
	@python3 scripts/check_self_contained.py

test-collection:
	@python3 -m pytest tests/ -v --tb=short

release:
	@bash scripts/release.sh $(ARGS)

convert:
	@bash scripts/convert.sh

clean:
	@rm -rf dist/
