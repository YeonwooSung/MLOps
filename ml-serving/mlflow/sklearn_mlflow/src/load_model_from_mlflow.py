import mlflow.sklearn

run_id = "<run_id>"
loaded_model = mlflow.sklearn.load_model(f"runs:/{run_id}/log_reg_model")
print("Loaded model:", loaded_model)
