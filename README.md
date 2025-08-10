# mlops-assignment

github-repo: https://github.com/2023AC05571WILP-BITS-PILANI/mlops-assignment  (code, data, model, pipeline)
Docker hub url : https://hub.docker.com/repositories/sanjaykumarcbits 
Docker image url : https://hub.docker.com/repository/docker/sanjaykumarcbits/iris-predictor/general (image)



📁 .github/workflows/
Contains GitHub Actions workflow YAML files to automate CI/CD tasks like testing, building, and deployment.
This pipeline automates code validation, containerization, and deployment for consistent and reliable delivery.
On every push to the main branch. It first runs a linting and testing job using flake8 and pytest to ensure code quality and correctness. If tests pass, it proceeds to build a Docker image of the project and pushes it to Docker Hub using credentials stored in GitHub Secrets. The final job deploys the Docker container locally on a Mac machine, pulling the latest image

📁 data/
Contains the Iris dataset (iris.csv) and its DVC tracking file for version control of data.

📁 iris-fastapi/
FastAPI-based microservice exposing ML model predictions via REST API, with tests and dependencies.
This FastAPI script sets up a REST API for predicting Iris flower species using MLflow-managed models. It randomly selects between Logistic Regression and Random Forest models based on accuracy, logs requests and predictions, and exposes Prometheus metrics for monitoring. The /predict endpoint accepts flower measurements and returns the predicted class. Logging is centralized in main.log, and Prometheus tracks request counts.

📁 mlflow_logs/
Stores MLflow experiment tracking data including models, metrics, parameters, and artifacts.

📁 mlops-assignment/
Holds a serialized scaler (scaler.pkl) used for model input standardization in the assignment.

📁 mounted_logs/
Contains runtime logs (main.log) for debugging and monitoring application behavior.

📁 prometheus_config/
Configuration file (prometheus.yml) for setting up Prometheus monitoring.

📁 src/
Modular source code for data preprocessing, transformation, and training ML models (Logistic & Random Forest).
Organized by ML pipeline stages. "preprocessing/load_data.py" for Data loading.
"transformation/transform_data.py" for Data transformation.
"training/train_model_logisticregression.py, train_model_randomforest.py" for  Model training scripts. "main.py"  

main.py
trains and logs two machine learning models—Logistic Regression and Random Forest—on the Iris dataset using MLflow. It loads and transforms the data, trains each model, evaluates accuracy, and logs parameters, metrics, and artifacts (including the scaler). Each model is registered in MLflow with a unique name for future retrieval and deployment. The scaler used for preprocessing is saved locally and also logged as an artifact. The workflow ensures reproducibility and traceability of experiments through MLflow’s tracking and model registry.

Dockerfile
builds a Docker image named iris-predictor from the current directory using the Dockerfile. The second command runs the container, mounts local directories for logs and MLflow tracking, and exposes the app on port 8000 for external access.

trigger_training_on_data_change.sh
continuously monitors the iris.csv file for changes using fswatch. When a change is detected, it automatically triggers the execution of a Python pipeline script (main.py) to reprocess or retrain the model.

          ┌──────────────┐
          │   Code Push  │      
          │  to 'main'   │
          └──────┬───────┘
                 │
        ┌────────▼────────┐
        │   lint-test job │
        │ - flake8 lint   │
        │ - pytest tests  │
        └────────┬────────┘
                 │
        ┌────────▼────────────┐
        │ docker-build-push   │
        │ - Build Docker image│
        │ - Push to Docker Hub│
        └────────┬────────────┘
                 │
        ┌────────▼────────────┐
        │     deploy job      │
        │ - Pull image        │
        │ - Run container     │
        └─────────────────────┘


        INSTRUCTIONS TO RUN:
        1. Open terminal and run start_all_services.sh. 
        2. This will start prediction service, mlflow ui, Prometheus and Grafana (grafana needs to be configured for source)
        3. query the precition service using : curl -X POST "http://localhost:8000/predict"   -H "Content-Type: application/json"   -d '{"sepal_length": 5.1, "sepal_width": 3.5, 
         "petal_length": 1.4, "petal_width": 0.2}’
        