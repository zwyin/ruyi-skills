.PHONY: test ci release sync convert clean check test-collection

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
	@bash scripts/release.sh

sync:
	@git subtree pull --prefix=skills/github-safe-publish https://github.com/zwyin/github-safe-publish.git master --squash
	@git subtree pull --prefix=skills/project-walkthrough https://github.com/zwyin/project-walkthrough-skill.git master --squash

convert:
	@bash scripts/convert.sh

clean:
	@rm -rf dist/
