# Simple Scikit-Learn Iris Classification Service

## Installation

Install following tools:

    - [Kubectl](https://kubernetes.io/docs/tasks/tools/)
    - [Helm](https://helm.sh/docs/intro/install/)
    - [Kubectx](https://github.com/ahmetb/kubectx)


## Deployment

1. Deploy simple K8S cluster with Kind:

```bash
$ kind create cluster --name kserve-demo
```

1 - 1. Switch to correct K8S context:

```bash
$ kubectx kind-kserve-demo
```

2. Install the Istio, KNative-Serving, and KServe:

```
# Install istio
curl -L https://istio.io/downloadIstio | ISTIO_VERSION=1.16.0 TARGET_ARCH=x86_64 sh -
istioctl install --set profile=default -y


# Install the Knative Serving component
export KNATIVE_VERSION="v1.7.2"
kubectl apply -f https://github.com/knative/serving/releases/download/knative-$KNATIVE_VERSION/serving-crds.yaml
kubectl apply -f https://github.com/knative/serving/releases/download/knative-$KNATIVE_VERSION/serving-core.yaml

# Install istio-controller for knative
kubectl apply -f https://github.com/knative/net-istio/releases/download/knative-v1.7.0/net-istio.yaml


helm repo add jetstack https://charts.jetstack.io
helm repo update
helm install cert-manager jetstack/cert-manager --namespace cert-manager --create-namespace --version v1.11.0 --set installCRDs=true


# create a namespace for model
kubectl create namespace kserve

# clone KServe repo
git clone git@github.com:kserve/kserve.git


# Install KServe Cutom Resource Definitions and KServe Runtimes into the model namespace in your cluster.
cd kserve
helm install kserve-crd charts/kserve-crd -n kserve
helm install kserve-resources charts/kserve-resources -n kserve
```

3. Create Inference Service

```bash
kubectl apply -n kserve -f - <<EOF
apiVersion: "serving.kserve.io/v1beta1"
kind: "InferenceService"
metadata:
  name: "sklearn-iris"
spec:
  predictor:
    model:
      modelFormat:
        name: sklearn
      storageUri: "gs://kfserving-examples/models/sklearn/1.0/model"
EOF
```

3 - 1. Monitor the status of the current deployment by getting the available pods in the namespace:

```bash
$ kubectl get pods -n kserve
```

3 - 2. Get status of all inference service deployments:

```
$ kubectl get isvc -A
```
