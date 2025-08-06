FROM python:3.9

WORKDIR /app

# Copy FastAPI app and dependencies
COPY ./iris-fastapi/api ./api
COPY ./iris-fastapi/requirements.txt ./requirements.txt


RUN chmod -R 777 /app/api

# Copy MLflow logs
COPY ./mlflow_logs ./api/mlflow_logs
RUN chmod -R 777 /app/api/mlflow_logs


RUN mkdir -p /app/mounted_logs && chmod -R 777 /app/mounted_logs

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
