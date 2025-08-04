import os
import importlib.util
import mlflow
import mlflow.sklearn
from src.preprocessing.load_data import load_data
from src.transformation.transform_data import transform_data
import joblib

# Set experiment name
mlflow.set_experiment("Iris_Training_Models")

# Load and transform data
data_path = os.path.join("data", "iris.csv")
data = load_data(data_path)
X_train, X_test, y_train, y_test, scaler = transform_data(data)

# Log common parameters
common_params = {
    "test_size": 0.2,
    "scaler": "StandardScaler"
}

# Iterate over all Python files in src/training/
training_dir = "src/training"
for filename in os.listdir(training_dir):
    if filename.endswith(".py") and filename != "__init__.py":
        module_name = filename[:-3]
        module_path = os.path.join(training_dir, filename)

        # Dynamically import the module
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Start MLflow run for each model
        with mlflow.start_run(run_name=module_name):
            mlflow.log_param("model_type", module_name)
            for param, value in common_params.items():
                mlflow.log_param(param, value)

            # Train model
            model_path = os.path.join("models", f"{module_name}_model.pkl")
            model = module.train_model(X_train, y_train, model_path)

            # Evaluate and log metrics
            accuracy = model.score(X_test, y_test)
            mlflow.log_metric("accuracy", accuracy)

            # Save and log artifacts
            scaler_path = os.path.join("models", f"{module_name}_scaler.pkl")
            joblib.dump(scaler, scaler_path)
            mlflow.log_artifact(model_path)
            mlflow.log_artifact(scaler_path)

            print(f"{module_name} model saved. Accuracy: {accuracy}")

