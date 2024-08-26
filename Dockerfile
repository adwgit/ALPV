FROM python:3.8-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
