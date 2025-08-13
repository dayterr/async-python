FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

RUN alembic init --t async migrations

RUN alembic revision --autogenerate -m 01_initial-db

RUN alembic upgrade head

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
