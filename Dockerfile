FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root && \
    poetry build

ENV PORT=8080
ENV PYTHONPATH=/app/src

CMD ["uvicorn", "friday.api.app:app", "--host", "0.0.0.0", "--port", "8080"]