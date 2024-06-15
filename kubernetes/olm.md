# Operator Lifecycle Manager (OLM)

The Operator Lifecycle Manager (OLM) extends Kubernetes to provide a declarative way to install, manage, and upgrade Operators on a cluster.

## Install OLM

The operator-sdk binary provides a command to easily install and uninstall OLM in a Kubernetes cluster.
See the [SDK installation guide](https://sdk.operatorframework.io/docs/installation/) on how to install operator-sdk tooling.

After you have the `operator-sdk` binary installed, you can install OLM on your cluster by running `operator-sdk olm install`.

```bash
operator-sdk olm install
```

## Installing an Operator using OLM 

When you install OLM, it comes packaged with a number of Operators developed by the community that you can install instantly.
You can use the packagemanifest api to see the operators available for you to install in your cluster:

```bash
kubectl get packagemanifest -n olm
```

To install the quay operator in the default namespace, first create an `OperatorGroup` for the default namespace:

```yaml
kind: OperatorGroup
apiVersion: operators.coreos.com/v1
metadata:
  name: og-single
  namespace: default
spec:
  targetNamespaces:
  - default
```

Then create the `OperatorGroup`:

```bash
kubectl apply -f operatorgroup.yaml
```
