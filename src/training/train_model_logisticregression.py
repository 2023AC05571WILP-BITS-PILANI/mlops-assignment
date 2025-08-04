from sklearn.linear_model import LogisticRegression
import joblib

def train_model(X_train, y_train, model_path):
    """Train and save a logistic regression model."""
    model = LogisticRegression(max_iter=200)
    model.fit(X_train, y_train)
    joblib.dump(model, model_path)
    return model

