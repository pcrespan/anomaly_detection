FROM python:3.13-slim

WORKDIR /app

COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

CMD ["sh", "-c", "python init_topic.py && python main.py"]