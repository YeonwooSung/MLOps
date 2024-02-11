import torch
import torch.nn as nn
from torch.utils import data
import torchvision
from sklearn.metrics import roc_auc_score, accuracy_score
import numpy as np
import mlflow
import mlflow.pytorch


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
batch_size = 256
num_classes = 10
learning_rate = 0.001
num_workers = 1

# Load the data
train_set = torchvision.datasets.MNIST(
    root="./data", train=True, download=True, transform=None
)
test_set = torchvision.datasets.MNIST(
    root="./data", train=False, download=True, transform=None
)
x_train, y_train = train_set.data.float(), train_set.targets
x_test, y_test = test_set.data.float(), test_set.targets

train_loader = data.DataLoader(
    dataset=train_set, batch_size=batch_size, shuffle=True, num_workers=num_workers
)
test_loader = data.DataLoader(
    dataset=test_set, batch_size=batch_size, shuffle=False, num_workers=num_workers
)

def to_one_hot(num_classes, labels):
    # one_hot = torch.zeros(labels.size(0), num_classes)
    # for f in range(len(labels)):
    #     one_hot[f, labels[f]] = 1
    # return one_hot
    return torch.nn.functional.one_hot(labels, num_classes)


y_train = to_one_hot(num_classes, y_train)
y_test = to_one_hot(num_classes, y_test)


class model(nn.Module):
    def __init__(self):
        super(model, self).__init__()
        # 1x28x28 -> 16x14x14
        self.conv1 = nn.Conv2d(1, 16, kernel_size=3, stride=2, padding=1, dilation=1)
        self.conv1_relu = nn.ReLU()
        # 16x14x14 -> 32x6x6
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, stride=2, padding=1, dilation=1)
        self.conv2_relu = nn.ReLU()
        # 32x6x6 -> 64x2x2
        self.conv3 = nn.Conv2d(32, 64, kernel_size=3, stride=2, padding=1, dilation=1)
        self.conv3_relu = nn.ReLU()
        # 64x2x2 -> 256
        self.flat1 = nn.Flatten()
        self.dense1 = nn.Linear(256, 128)
        self.dense1_relu = nn.ReLU()
        self.dense2 = nn.Linear(128, 64)
        self.dense2_relu = nn.ReLU()
        self.dense3 = nn.Linear(64, num_classes)
        self.softmax = nn.Softmax()

    def forward(self, x):
        x = self.conv1_relu(self.conv1(x))
        x = self.conv2_relu(self.conv2(x))
        x = self.conv3_relu(self.conv3(x))
        x = self.flat1(x)
        x = self.dense1_relu(self.dense1(x))
        x = self.dense2_relu(self.dense2(x))
        x = self.dense3(x)
        x = self.softmax(x)
        return x


model = model().to(device)
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
criteron = nn.BCELoss()

num_epochs = 5
for f in range(num_epochs):
    for batch_num, minibatch in enumerate(train_loader):
        x, y = minibatch
        output = model(torch.Tensor(x).to(device))
        loss = criteron(output, y)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()


# Log metrics with MLflow
mlflow.set_experiment("pytorch_mnist")
with mlflow.start_run():
    mlflow.log_param("num_epochs", num_epochs)
    mlflow.log_param("learning_rate", learning_rate)
    mlflow.log_param("batch_size", batch_size)
    mlflow.log_param("num_workers", num_workers)

    # Log metrics
    y_pred = model(x_test.to(device))
    y_pred = y_pred.cpu().detach().numpy()
    y_test = y_test.numpy()
    auc = roc_auc_score(y_test, y_pred)
    accuracy = accuracy_score(y_test, y_pred)
    mlflow.log_metric("auc", auc)
    mlflow.log_metric("accuracy", accuracy)

    # Log model
    mlflow.pytorch.log_model(model, "PyTorch_MNIST")
mlflow.end_run()

# Model registry
loaded_model = mlflow.pytorch.load_model("runs:/<run_id>/PyTorch_MNIST")
preds = loaded_model(x_test.to(device))
preds = preds.cpu().detach().numpy()
eval_acc = accuracy_score(y_test, preds)
auc_score = roc_auc_score(y_test, preds)
print(f"Eval Accuracy: {eval_acc}")
print(f"AUC Score: {auc_score}")
