
docker build -t iris-predictor .

docker run --rm -v "$(pwd)/mounted_logs:/app/mounted_logs"  -v "$(pwd)/mlflow_logs:$(pwd)/mlflow_logs" -p 8000:8000 iris-predictor  
