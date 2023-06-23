FROM python:3.8-slim-bookworm
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8082
CMD ["python3", "app.py"]