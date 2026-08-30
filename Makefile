.PHONY: install lab api mcp mcp-install up docker-build docker-up test lint fmt format-check check clean

install:
	pip install -e ".[all,api,mcp]"

lab:
	streamlit run app/main.py

api:
	uvicorn signal_processing.api:app --reload --port 8000

mcp:
	signal-process-mcp

mcp-install:            # Registers with Claude Desktop / any MCP-aware host
	uv run mcp install src/signal_processing/mcp_server.py

up:                     # Starts all three services locally via Caddy and launcher.sh
	./launcher.sh

docker-build:
	docker build -t signal-lab .

docker-up:
	docker run --rm -p 7860:7860 signal-lab

test:
	pytest

lint:
	ruff check src tests app

fmt:
	ruff format src tests app

format-check:
	ruff format --check src tests app

check: lint format-check test

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	find . -type d -name ".ruff_cache" -delete
