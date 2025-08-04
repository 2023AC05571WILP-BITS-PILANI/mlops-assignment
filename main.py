import os
import mlflow
import mlflow.sklearn
from src.preprocessing.load_data import load_data
from src.transformation.transform_data import transform_data
from src.training.train_model_logisticregression import train_model
import joblib

mlflow.set_tracking_uri(f"file://{os.getcwd()}/mlops-assignment/mlflow_logs")
# Set experiment name
mlflow.set_experiment("Iris_Logistic_Regression")
with mlflow.start_run():
    # Load data
    data_path = os.path.join(f"{os.getcwd()}/mlops-assignment/data", "iris.csv")
    data = load_data(data_path)

    # Transform data
    X_train, X_test, y_train, y_test, scaler = transform_data(data)

    # Log parameters
    mlflow.log_param("model_type", "LogisticRegression")
    mlflow.log_param("test_size", 0.2)
    mlflow.log_param("scaler", "StandardScaler")

    # Train model
    model_path = os.path.join(f"{os.getcwd()}/mlops-assignment/models", "logistic_model.pkl")
    model = train_model(X_train, y_train, model_path)

    # Evaluate and log metrics
    accuracy = model.score(X_test, y_test)
    mlflow.log_metric("accuracy", accuracy)

    # Save and log artifacts
    scaler_path = os.path.join(f"{os.getcwd()}/mlops-assignment/models", "scaler.pkl")
    joblib.dump(scaler, scaler_path)
    mlflow.log_artifact(model_path)
    mlflow.log_artifact(scaler_path)

    print(f"Model and scaler saved. Accuracy: {accuracy}")

