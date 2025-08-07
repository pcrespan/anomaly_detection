FROM python:3.13-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED=1

EXPOSE 9000

CMD ["gunicorn", "-w", "10", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:9000"]