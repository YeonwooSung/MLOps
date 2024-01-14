# Prometheus Stack

## Install and setup

```bash
# helm repo add
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts

# helm repo update
helm repo update

# helm install
# helm install [RELEASE_NAME] prometheus-community/kube-prometheus-stack
helm install prom-stack prometheus-community/kube-prometheus-stack
# 모든 values 는 default 로 생성됨
# https://github.com/prometheus-community/helm-charts/blob/main/charts/kube-prometheus-stack/values.yaml
# 실무에서 admin password나 ingress, storage class, resource 등을 수정해야 할 때에는 위의 url을 참고해 charts를 clone하고
# clone한 디렉토리에서 values.yaml 을 수정하여 git 으로 환경별 히스토리 관리해야 함

# check if installed successfully (-w for watch)
kubectl get pod -w

# run the port-forward command
kubectl port-forward svc/prom-stack-grafana 9000:80
kubectl port-forward svc/prom-stack-kube-prometheus-prometheus 9091:9090
```

### Troubleshooting

If you use docker desktop with minikube, you may not be able to run port-forwarding.
For this, you could run the following command to access the service.

```bash
minikube service prom-stack-grafana --url

minikube service prom-stack-kube-prometheus-prometheus --url
```
