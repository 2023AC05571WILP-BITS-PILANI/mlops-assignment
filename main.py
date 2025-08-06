import os
import mlflow
import mlflow.sklearn
import pandas as pd
import joblib
from src.preprocessing.load_data import load_data
from src.transformation.transform_data import transform_data
from src.training.train_model_logisticregression import train_model_lr
from src.training.train_model_randomforest import train_model_rf
from mlflow.models import infer_signature


mlflow.sklearn.autolog(disable=True)
# Set MLflow tracking URI
tracking_dir = os.path.join(os.getcwd(), "mlflow_logs")
mlflow.set_tracking_uri(f"file://{tracking_dir}")

# Set experiment name
mlflow.set_experiment("Iris_Logistic_Regression")

with mlflow.start_run():

    # Load data
    data_path = os.path.join(os.getcwd(), "data", "iris.csv")
    data = load_data(data_path)

    # Transform data
    X_train, X_test, y_train, y_test, scaler = transform_data(data)

    # Log parameters
    mlflow.log_param("model_type", "LogisticRegression")
    mlflow.log_param("test_size", 0.2)
    mlflow.log_param("scaler", "StandardScaler")

    # Train model
    model = train_model_lr(X_train, y_train)

    # Evaluate and log metrics
    accuracy = model.score(X_test, y_test)
    mlflow.log_metric("accuracy", accuracy)

    # Log model using MLflow's model logging API
    input_example = pd.DataFrame(X_train[:1], columns=data.columns[:-1])
    signature = infer_signature(X_train, model.predict(X_train))
    
    mlflow.sklearn.log_model(
        sk_model=model,
        name="name",  # Ensures model is logged to artifacts/model/
        input_example=input_example,
        signature=signature,
        registered_model_name="Iris_Logistic_Regression_Model"  # Registers the model with a name
    )


    scaler_path = os.path.join("mlops-assignment", "scaler.pkl")
    os.makedirs(os.path.dirname(scaler_path), exist_ok=True)
    joblib.dump(scaler, scaler_path)
    mlflow.log_artifact(scaler_path, artifact_path="scaler")  # Logs to artifacts/scaler/

    print(f"Model and scaler saved. Accuracy: {accuracy}")


mlflow.set_experiment("Iris_Random_Forest")

with mlflow.start_run():

    # Load data
    data_path = os.path.join(os.getcwd(), "data", "iris.csv")
    data = load_data(data_path)

    # Transform data
    X_train, X_test, y_train, y_test, scaler = transform_data(data)

    # Log parameters
    mlflow.log_param("model_type", "RandomForestClassifier")
    mlflow.log_param("test_size", 0.2)
    mlflow.log_param("scaler", "StandardScaler")

    # Train model
    model = train_model_rf(X_train, y_train)

    # Evaluate and log metrics
    accuracy = model.score(X_test, y_test)
    mlflow.log_metric("accuracy", accuracy)

    # Log model using MLflow's model logging API
    input_example = pd.DataFrame(X_train[:1], columns=data.columns[:-1])
    signature = infer_signature(X_train, model.predict(X_train))
    
    mlflow.sklearn.log_model(
        sk_model=model,
        name="name",  # Ensures model is logged to artifacts/model/
        input_example=input_example,
        signature=signature,
        registered_model_name="Iris_Random_Forest_Model"  # Registers the model with a name
    )


    scaler_path = os.path.join("mlops-assignment", "scaler.pkl")
    os.makedirs(os.path.dirname(scaler_path), exist_ok=True)
    joblib.dump(scaler, scaler_path)
    mlflow.log_artifact(scaler_path, artifact_path="scaler")  # Logs to artifacts/scaler/

    print(f"Model and scaler saved. Accuracy: {accuracy}")
