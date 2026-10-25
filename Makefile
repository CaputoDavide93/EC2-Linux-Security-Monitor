# One entry point for the checks CI runs. `make check` before every push.
.PHONY: check lint diagram screenshots social-preview

check: lint ## Everything CI checks, except the systemd calendar validation
	python3 tools/gen_diagram.py --check

lint: ## bash -n, shellcheck, and the config file sources cleanly
	bash -n security-monitor.sh
	bash -n security-manager.sh
	shellcheck --severity=warning security-monitor.sh security-manager.sh
	bash -n security-monitor.conf && ( set -eu; . ./security-monitor.conf )

diagram: ## Redraw docs/assets/*.svg
	python3 tools/gen_diagram.py

screenshots: ## Retake docs/assets/screenshots/ from the real dashboard (needs Docker, not CI)
	test -x .venv-screenshots/bin/python || ( \
		uv venv -q --python 3.14 .venv-screenshots && \
		VIRTUAL_ENV=.venv-screenshots uv pip install -q -r tools/screenshots/requirements.txt )
	.venv-screenshots/bin/python -m playwright install chromium
	.venv-screenshots/bin/python tools/screenshots/take_screenshots.py

social-preview: ## Redraw docs/assets/social-preview.png (not CI)
	test -x .venv-screenshots/bin/python || $(MAKE) screenshots
	.venv-screenshots/bin/python tools/social_preview.py
