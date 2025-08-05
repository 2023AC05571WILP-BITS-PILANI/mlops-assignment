import time
from fastapi import FastAPI
import numpy as np
from pydantic import BaseModel
import uvicorn
import os
import mlflow
import pandas as pd
import logging
from sklearn import datasets



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

#time.sleep(100000)
try:
    mlflow.set_tracking_uri("file:///app/api/mlflow_logs")

    mlflow.set_experiment("Iris_Logistic_Regression")
    runs = mlflow.search_runs(order_by=["metrics.accuracy DESC"])
    if not runs.empty:
        best_run_id = runs.iloc[0]["artifact_uri"]
        logging.info(f"Best run ID: {best_run_id}")
        best_run_id = runs.iloc[0]["run_id"]
        logging.info(f"Best run ID: {best_run_id}")
        best_run_id = runs.iloc[0]["run_id"]
        model_uri = f"runs:/{best_run_id}/model"
        model_name = "Iris_Logistic_Regression_Model"
        model_version = "2"
        model = mlflow.pyfunc.load_model(f"models:/{model_name}/{model_version}")
        logger.info(f"Loaded model from URI: {model}")
    else:
        current_dir = os.getcwd()
        mlflow_logs_path = os.path.join(current_dir, 'mlflow_logs')

        logging.error("MLflow setup failed: No runs found for the experiment.")
        logging.error(f"Current working directory: {current_dir}")
        logging.error(f"Expected MLflow logs directory: {mlflow_logs_path}")

        if os.path.exists(mlflow_logs_path):
            try:
                contents = os.listdir(mlflow_logs_path)
                logging.info(f"Contents of MLflow logs directory: {contents}")
                print("MLflow logs directory contents:")
                for item in contents:
                    print(f"- {item}")
            except Exception as e:
                logging.error(f"Error reading MLflow logs directory: {e}")
        else:
            logging.warning("MLflow logs directory does not exist.")

        best_run_id = None  # or handle accordingly
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
#curl -X POST "http://localhost:8000/predict" -H "Content-Type: application/json" -d '{"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}'
#