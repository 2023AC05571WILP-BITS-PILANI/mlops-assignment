from sklearn.ensemble import RandomForestClassifier
import joblib

def train_model_rf(X_train, y_train, model_path=None):
    """Train and optionally save a random forest model."""
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    if model_path:
        joblib.dump(model, model_path)

    return model
