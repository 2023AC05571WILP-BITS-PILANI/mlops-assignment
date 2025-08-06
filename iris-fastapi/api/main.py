from fastapi import FastAPI
import numpy as np
from pydantic import BaseModel
import os
import mlflow
import logging


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


try:
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
        logger.info(f"Model version {v.version} has accuracy: {accuracy}")
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_version = v.version

    if best_version is None:
        logger.error("No valid model version found with accuracy metric.")

    model_name = "Iris_Logistic_Regression_Model"
    model_version = best_version
    model = mlflow.pyfunc.load_model(f"models:/{model_name}/{model_version}")
    logger.info(f"Loaded model from URI: {model}")

except Exception as e:
    logging.error(f"Error setting up MLflow: {e}")
    best_run_id = None

# FastAPI app
app = FastAPI()


class Input(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float


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
        prediction = model.predict(features)
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
