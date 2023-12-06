import mlflow
import mlflow.sklearn

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score


# Load the Iris dataset
data = load_iris()
X = data.data
y = data.target

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create and train a RandomForestClassifier
clf = RandomForestClassifier(n_estimators=100)
clf.fit(X_train, y_train)

# Make predictions
y_pred = clf.predict(X_test)

# Log metrics
accuracy = accuracy_score(y_test, y_pred)
mlflow.log_metric("accuracy", accuracy)

# Log parameters
mlflow.log_params({"n_estimators": 100, "random_state": 42})

# Log the model as an artifact
mlflow.sklearn.log_model(clf, "model")
