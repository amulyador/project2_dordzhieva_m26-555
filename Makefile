install:
	uv sync

run:
	uv run python -m primitive_db.main

lint:
	uv run ruff check .  
