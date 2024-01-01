import numpy as np
import pandas as pd

import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

# import sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import KFold

import mlflow


def train(model, x_train, y_train):
    model.fit(x_train, y_train)
    train_acc = model.score(x_train, y_train)
    mlflow.log_metric("train_acc", train_acc)
    print(f"Train Accuracy: {train_acc:.3%}")
    return model


def evaluate(model, x_test, y_test):
    preds = model.predict(x_test)
    test_acc = model.score(x_test, y_test)
    mlflow.log_metric("test_acc", test_acc)
    print(f"Test Accuracy: {test_acc:.3%}")

    cm = confusion_matrix(y_test, preds)
    plt.figure(figsize=(5, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False)
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title("Confusion Matrix")
    plt.savefig("confusion_matrix.png")

    mlflow.log_artifact("confusion_matrix.png")

    return test_acc, preds


RANDOM_SEED = 42

print("MLflow Version:", mlflow.__version__)

data_path = "data/creditcard.csv"
df = pd.read_csv(data_path)
df = df.drop("Time", axis=1)

normal = df[df.Class == 0].sample(frac=0.5, random_state=RANDOM_SEED).reset_index(drop=True)
anomaly = df[df.Class == 1]

print("Normal shape:", normal.shape)
print("Anomaly shape:", anomaly.shape)

_, normal_test = train_test_split(normal, test_size=0.2, random_state=RANDOM_SEED)
_, anomaly_test = train_test_split(anomaly, test_size=0.2, random_state=RANDOM_SEED)
normal_train, normal_validate = train_test_split(normal, test_size=0.25, random_state=RANDOM_SEED)
anomaly_train, anomaly_validate = train_test_split(anomaly, test_size=0.25, random_state=RANDOM_SEED)

x_train = pd.concat([normal_train, anomaly_train])
x_validate = pd.concat([normal_validate, anomaly_validate])
x_test = pd.concat([normal_test, anomaly_test])

y_train = np.array(x_train["Class"])
y_validate = np.array(x_validate["Class"])
y_test = np.array(x_test["Class"])

x_train = x_train.drop("Class", axis=1)
x_validate = x_validate.drop("Class", axis=1)
x_test = x_test.drop("Class", axis=1)


scaler = StandardScaler()
scaler.fit(pd.concat((normal, anomaly)).drop("Class", axis=1))

x_train = scaler.transform(x_train)
x_validate = scaler.transform(x_validate)
x_test = scaler.transform(x_test)


# sk_model = LogisticRegression(random_state=RANDOM_SEED, max_iter=1000, solver="newton-cg")
mlflow.set_experiment("sklearn_creditcard_broad_search")

anomaly_weights = [1, 5, 10, 15]
num_folds = 5
kf = KFold(n_splits=num_folds, random_state=RANDOM_SEED, shuffle=True)

logs = []
for f in range(len(anomaly_weights)):
    fold = 1
    accuracies = []

    for train, test in kf.split(x_train):
        with mlflow.start_run():
            print(f"Fold #{fold}")
            fold += 1

            sk_model = LogisticRegression(
                random_state=RANDOM_SEED,
                max_iter=1000,
                solver="newton-cg",
                class_weight={0: 1, 1: anomaly_weights[f]}
            )
            sk_model = train(sk_model, x_train[train], y_train[train])
            test_acc, preds = evaluate(sk_model, x_train[test], y_train[test])
            accuracies.append(test_acc)

            print('-' * 20)
            print(f"Fold {fold} anomaly weight {anomaly_weights[f]}")
            print(f"Test Accuracy: {test_acc:.3%}")

        fold += 1
        mlflow.end_run()
    print('=' * 20)
    print(f"Anomaly weight {anomaly_weights[f]}")
    print(f"Average accuracy: {np.mean(accuracies):.3%}")
    print('=' * 20)
