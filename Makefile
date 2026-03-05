.PHONY: bootstrap test dev vps web

bootstrap:
	./scripts/bootstrap.sh

test:
	. .venv/bin/activate && pytest

dev:
	./scripts/run-dev.sh --config config/defaults.yaml

vps:
	./scripts/run-vps.sh --config config/defaults.yaml --inventory inventory/vps.example.ini --print-only

web:
	. .venv/bin/activate && python -m webapp.app
