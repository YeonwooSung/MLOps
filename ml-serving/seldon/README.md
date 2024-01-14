# Seldon

Seldon is an open source platform for deploying machine learning models on a Kubernetes cluster.
It is designed to help engineers and data scientists deploy their ML models into production safely, securely and at scale.

Seldon uses flask for handling REST requests and gRPC for handling gRPC requests.

## Pre-requisites

Seldon requires a running Kubernetes cluster with kubectl configured to access it.
Also, you should be familiar with the Kubernetes, otherwise it will be hard to understand what is going on.

## Seldon with K8S

### Custom Resources

Custom Resources is a Kubernetes feature that allows to extend Kubernetes API with new objects.
CR objects are stored in the Kubernetes API server and can be managed using kubectl.
CRD (Custom Resource Definition) is a definition of a new CR object which defines the custom controller that manages the CR object.

So, the CR (Custom Resource) does not managed by the Kubernetes as default, but K8S can be extended with custom controllers that will manage the CR objects.

### Operator pattern

The operator in kubernetes is a kubernetes API client that plays the role of a controller for the CR objects.
The operator automatically manages the CR objects and the resources that are related to the CR objects.

## Instruction for sample

```bash
# Create a namespace for seldon-system
kubectl create namespace seldon-system

# Install Seldon Core
helm install seldon-core seldon-core-operator \
    --repo https://storage.googleapis.com/seldon-charts \
    --set usageMetrics.enabled=true \
    --namespace seldon-system

# Check the status of the pods (if failed, cannot continue to the next step)
kubectl get pods -n seldon-system

# create the custom deployment
kubectl apply -f sample.yaml
```
