.PHONY: install test lint format typecheck demo lab docker clean

install:
	python -m pip install -e ".[all]"

test:
	pytest

lint:
	ruff check .

format:
	ruff format .

typecheck:
	mypy src

demo:
	python examples/basic_signal.py

lab:
	streamlit run app/main.py

docker:
	docker compose up --build

clean:
	rm -rf build dist *.egg-info .pytest_cache .mypy_cache .ruff_cache htmlcov
