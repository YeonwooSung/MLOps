# Common Problems and Solutions for K8S Pod Lifecycles

## Q1. Pods are not in Ready state.
- Check that the Readiness probe is passing.

## Q2. New pods never become ready.
- Check for app issues.

## Q3. Pod restarting unexpectedly.
- Fix or remove Liveness probes.

## Q4. Pod in CrashLoopBackoff.
- Inspect container logs & fix app issues.

## Q5. High latency for requests to new pods.
- Lack of pre-warming of the application.
- Try pre-warming app or use "slow_start".

## Q6. Pods flapping between ready/not ready; in and out of ALB target groups.
- Gate rush sends too much traffic (no threads?), causing Pod to fail readiness.
