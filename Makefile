.PHONY: up test lint
up:
	docker compose up -d --build
test:
	pytest backend/tests -q
lint:
	ruff check backend
