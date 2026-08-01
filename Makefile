.PHONY: bootstrap test dev dev-check vps web

bootstrap:
	./scripts/bootstrap.sh

test:
	uv run pytest

dev:
	./scripts/run-dev.sh --config config/defaults.yaml

dev-check:
	./scripts/run-dev.sh --config config/defaults.yaml --check

vps:
	./scripts/run-vps.sh --config config/defaults.yaml --inventory inventory/vps.example.ini --print-only

web:
	uv run python -m webapp.app
