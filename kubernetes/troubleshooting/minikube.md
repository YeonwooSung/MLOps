# Minikube Troubleshooting

## Table of Contents

* [1. Service not accessible](#1-service-not-accessible)

## 1. Service not accessible

`minikube` doesn’t allow to access the external IP`s directly for the service of a kind NodePort or LoadBalancer.
So, even if you have a service of type NodePort or LoadBalancer, you can’t access it directly via the external IP.

Especially, if you are using docker engine for minikube with docker desktop on Darwin kernel (Mac OS), even the `minikube ip` will not work.
To access the service, you need to use the `minikube service <service-name>` command.

```bash
# To access the service "my-nginx" run the following command:
minikube service my-nginx --url
```
