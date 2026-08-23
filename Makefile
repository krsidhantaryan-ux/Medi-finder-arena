.PHONY: help install dev test seed docker-up docker-down clean

help:
	@echo "MediFinder Development Commands:"
	@echo "  make install     Install all backend dependencies"
	@echo "  make dev         Run the development server"
	@echo "  make test        Run the Pytest test suite"
	@echo "  make seed        Seed sample demo pharmacies, medications, and users"
	@echo "  make docker-up   Start MongoDB and MediFinder via Docker Compose"
	@echo "  make docker-down Stop running containers"
	@echo "  make clean       Clean temporary cache files"

install:
	pip install -r backend/requirements.txt
	pip install -r backend/requirements-dev.txt

dev:
	python3 run.py

test:
	pytest backend/tests -v

seed:
	python3 -m backend.src.seed

docker-up:
	docker-compose up --build -d

docker-down:
	docker-compose down

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov
