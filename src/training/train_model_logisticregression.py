def train_model_lr(X_train, y_train, model_path=None):
    from sklearn.linear_model import LogisticRegression
    import joblib
    import os

    model = LogisticRegression()
    model.fit(X_train, y_train)

    if model_path:
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        joblib.dump(model, model_path)

    return model
