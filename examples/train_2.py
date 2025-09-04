# The data set used in this example is from http://archive.ics.uci.edu/ml/datasets/Wine+Quality
# P. Cortez, A. Cerdeira, F. Almeida, T. Matos and J. Reis.
# Modeling wine preferences by data mining from physicochemical properties. In Decision Support Systems, Elsevier, 47(4):547-553, 2009.

import os
import warnings
import sys
from dotenv import load_dotenv

import mlflow.sklearn
import pandas as pd
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from urllib.parse import urlparse
import mlflow
import mlflow.sklearn
from mlflow.models import infer_signature
import mlflow.data
from mlflow.tracking import MlflowClient
import json
import logging

logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)

# Load environment variables from a .env file
load_dotenv('./example.env')

mlflow_user = os.getenv("MLFLOW_USER")
mlflow_password = os.getenv("MLFLOW_PASSWORD")
mlflow_domain = os.getenv("MLFLOW_DOMAIN")

# Set MLflow tracking URI if domain is provided
if mlflow_domain and mlflow_user and mlflow_password:
    # mlflow_full_url = f"http://{mlflow_user}:{mlflow_password}@{mlflow_domain}"
    mlflow_full_url = f"http://{mlflow_domain}"
    mlflow.set_tracking_uri(mlflow_full_url)

# Set credentials if provided
if mlflow_user and mlflow_password:
    os.environ["MLFLOW_TRACKING_USERNAME"] = mlflow_user
    os.environ["MLFLOW_TRACKING_PASSWORD"] = mlflow_password

experiment_name = os.getenv("EXPERIMENT_NAME")
while experiment_name is None or experiment_name=='':
    experiment_name=input("""Introduce the name of the experiment 
                                \ror exit.""")

if experiment_name in ['exit', "e"]:
    exit(-1)

def eval_metrics(actual, pred):
    precision = precision_score(actual, pred, average='weighted')
    recall = recall_score(actual, pred, average='weighted')
    f1 = f1_score(actual, pred, average='weighted')
    confusion = confusion_matrix(actual, pred)
    return precision, recall, f1, confusion

def update_if_not_exist_mlflow_dataset(df: pd.DataFrame, experiment_name: str):
    client = MlflowClient(mlflow_full_url)
    experiment = client.get_experiment_by_name(experiment_name)
    if experiment is None:
        logger.error("Experiment not found: %s", experiment_name)
        return False

    # Check if the dataset is logged
    runs = client.search_runs(experiment_ids=[experiment.experiment_id])
    i = 0
    found = False
    while i<len(runs) and not found:
        run = runs[i]
        try:
            client.download_artifacts(run.info.run_id, "data/dataset.csv", dst_path="old_dataset")
            old_data = pd.read_csv("old_dataset.csv")
            if old_data.equals(df):
                logger.info("Dataset already exists in MLflow.")
                with open("reference.txt", "w") as f:
                    f.write(run.info.run_id)
                mlflow.log_artifact("reference.txt", artifact_path="data")
                found = True
        except Exception as e:
            ...
        i+=1

    if not found:
        mlflow.log_artifact("dataset.csv", artifact_path="data")

def confusion_to_json(confusion_matrix, filename="confusion_matrix.json"):
    contents = [[int(elem) for elem in row] for row in confusion_matrix]
    with open(filename, 'w') as f:
        json.dump(contents, f)


if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    np.random.seed(40)

    mlflow.set_experiment(experiment_name)

    # Read the wine-quality csv file from the URL
    csv_url = (
        "./bad_wine.csv"
    )
    try:
        data = pd.read_csv(csv_url, sep=",")
    except Exception as e:
        logger.exception(
            "Unable to download training & test CSV, check your internet connection. Error: %s", e
        )

    X = data.drop(["quality"], axis=1)
    y = data[["quality"]]

    # Split the data into training and test sets. (0.75, 0.25) split.
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

    dataset_registry = pd.concat([X_train, y_train], axis=1)
    dataset_mlfow = mlflow.data.from_pandas(
        pd.concat([X, y], axis=1), name="wine-quality-white", targets="quality"
    )

    X.to_csv("./dataset.csv", index=False)

    print(len(y_test))

    for i in range(10):
        with mlflow.start_run() as run:
            model = RandomForestClassifier()
            model.fit(X_train, y_train)

            y_pred = model.predict(X_test)

            precision, recall, f1, confusion = eval_metrics(y_test, y_pred)

            print(f"  Precision: {precision}")
            print(f"  Recall: {recall}")
            print(f"  F1 Score: {f1}")
            print(f"  Confusion Matrix:\n{confusion}")
            signature = infer_signature(X_train, y_train)
            mlflow.log_param("Seed", model.random_state)
            mlflow.log_metric("precision", precision)
            mlflow.log_metric("recall", recall)
            mlflow.log_metric("f1", f1)

            confusion_to_json(confusion)
            mlflow.log_artifact("confusion_matrix.json", artifact_path="metrics")
            os.remove("confusion_matrix.json")

            mlflow.log_input(dataset_mlfow)
            update_if_not_exist_mlflow_dataset(dataset_registry, experiment_name)

            tracking_url_type_store = urlparse(mlflow.get_tracking_uri()).scheme
            print(mlflow.get_artifact_uri())

            mlflow.sklearn.log_model(model, "model", signature=signature)

    os.remove("dataset.csv")