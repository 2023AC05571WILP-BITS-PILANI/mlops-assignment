import random
from fastapi import FastAPI, Request, Response
import numpy as np
from pydantic import BaseModel
import os
import mlflow
import logging
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST


# Setup logging
LOG_DIR = './mounted_logs'
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, 'main.log')
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


logger = logging.getLogger(__name__)


def get_model():
    try:
        if (random.randint(1, 100) % 2) == 0:
            mlflow.set_tracking_uri("file:///app/api/mlflow_logs")
            mlflow.set_experiment("Iris_Logistic_Regression")
            client = mlflow.MlflowClient()
            # Define your registered model name
            model_name = "Iris_Logistic_Regression_Model"

            # Search all versions of the model
            versions = client.search_model_versions(f"name='{model_name}'")

            best_version = None
            best_accuracy = -1

            for v in versions:
                run_id = v.run_id
                metrics = client.get_run(run_id).data.metrics
                accuracy = metrics.get("accuracy", -1)
                if accuracy > best_accuracy:
                    best_accuracy = accuracy
                    best_version = v.version

            if best_version is None:
                logger.error(
                    "No valid model version found with accuracy metric.")

            model_version = best_version
            model = mlflow.pyfunc.load_model(
                f"models:/{model_name}/{model_version}")
            logger.info("Prediction using : Iris_Logistic_Regression_Model")
        else:
            mlflow.set_tracking_uri("file:///app/api/mlflow_logs")
            mlflow.set_experiment("Iris_Random_Forest")
            client = mlflow.MlflowClient()
            # Define your registered model name
            model_name = "Iris_Random_Forest_Model"

            # Search all versions of the model
            versions = client.search_model_versions(f"name='{model_name}'")

            best_version = None
            best_accuracy = -1

            for v in versions:
                run_id = v.run_id
                metrics = client.get_run(run_id).data.metrics
                accuracy = metrics.get("accuracy", -1)
                if accuracy > best_accuracy:
                    best_accuracy = accuracy
                    best_version = v.version

            if best_version is None:
                logger.error(
                    "No valid model version found with accuracy metric.")

            model_version = best_version
            model = mlflow.pyfunc.load_model(
                f"models:/{model_name}/{model_version}")
            logger.info("Prediction using : Iris_Random_Forest_Model")

    except Exception as e:
        logging.error(f"Error setting up MLflow: {e}")
    return model


# FastAPI app
app = FastAPI()


class Input(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float


# Create a Prometheus Counter metric
REQUEST_COUNT = Counter(
    "app_requests_total", "Total number of requests", ["method", "endpoint"]
)


@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    response = await call_next(request)
    REQUEST_COUNT.labels(method=request.method,
                         endpoint=request.url.path).inc()
    return response


@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/predict")
def predict(input: Input):
    features = np.array([[
        input.sepal_length,
        input.sepal_width,
        input.petal_length,
        input.petal_width
    ]])
    logger.info(f"Received prediction request with features: {features}")
    try:
        prediction = get_model().predict(features)
        predicted_class = prediction[0]
        logger.info(f"Prediction result: {predicted_class}")
        return {"prediction": predicted_class}
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        return {"error": "Prediction failed"}


# Uncomment to run locally
# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)
# curl -X POST "http://localhost:8000/predict" \
# -H "Content-Type: application/json" \
# -d '{"sepal_length": 5.1, "sepal_width": 3.5, \
#  "petal_length": 1.4, "petal_width": 0.2}'
#
