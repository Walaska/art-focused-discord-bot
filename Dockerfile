FROM python:3.9
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
COPY .env main/.env
CMD ["python", "loader.py"]
