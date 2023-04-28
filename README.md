# k8s-fast (kubernetes-fastapi)

Python FastAPI with Dockerfile and configuration for Kubernetes

## Python Virtual Environment 

https://docs.python.org/3/tutorial/venv.html 

    you@you % python3 -m venv venv
    you@you % source venv/bin/activate
    (venv) you@you % 

## Development setup

To run (in isolation), either:

Run from active Python environment using `uvicorn`:

    pip install -r requirements.txt
    uvicorn service.main:app --host 0.0.0.0 --port 8080 --reload

Or

Build and run the Docker container:

    docker build -t clam004/k8s-fast:1.0 .
    docker run -d -p 8080:8080 --name k8s-fast clam004/k8s-fast:1.0

Navigate to http://localhost:8080/docs to test the API.

![Test drive the API](./resources/openapi.png)

The API responds with a greeting, and the result of a long-running calculation of the largest prime factor of a random integer. You should see a response body similar to:

    {
      "message1": "Hello, world!",
      "message2": "The largest prime factor of 1462370954730 is 398311. Calculation took 0.006 seconds.",
      "n": 1462370954730,
      "largest_prime_factor": 398311,
      "elapsed_time": 0.0057561397552490234
    }

## Before using Kubernetes Push the container image to Docker Hub

If you dont already, you need a DockerHUb account and to be signed-in in terminal

    docker login

push the container to Docker Hub, and change all references to the image accordingly. Replace "clam004" with your Docker Hub ID:

    docker push clam004/k8s-fast:1.0

You may also need to make the image public as well.

## get minikube

https://minikube.sigs.k8s.io/docs/start/ 

### you need a metrics server for horizontal pod scaling

https://www.bogotobogo.com/DevOps/Docker/Docker-Kubernetes-Horizontal-Pod-Autoscaler.php

metrics-server monitoring needs to be deployed in the cluster to provide metrics via the resource metrics API, as Horizontal Pod Autoscaler uses this API to collect metrics:

    (venv) you@you % minikube addons enable metrics-server

or

    (venv) you@you % kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/download/v0.4.1/components.yaml 

You need to edit this file 

    (venv) you@you % kubectl edit deployments.apps -n kube-system metrics-server  

to include `- --kubelet-insecure-tls=true` in the location below.

```
    spec:
      containers:
      - args:
        - --cert-dir=/tmp
        - --secure-port=4443
        - --kubelet-insecure-tls=true
        - --kubelet-preferred-address-types=InternalIP,ExternalIP,Hostname
```

## Kubernetes deployment

    kubectl apply -f api.yaml

If working locally, e.g. using `minikube`, use port forwarding to expose the service:

    (venv) you@you % kubectl apply -f api.yaml
    service/kf-api-svc created
    deployment.apps/kf-api created
    (venv) you@you %  kubectl port-forward service/kf-api-svc 8080
    Forwarding from 127.0.0.1:8080 -> 8080
    Forwarding from [::1]:8080 -> 8080
    Handling connection for 8080

To scale the deployment, apply a HorizontalPodAutoscaler. Either:

    kubectl apply -f autoscale.yaml

note sure which order these go in

    (venv) you@you % kubectl apply -f api.yaml
    service/kf-api-svc created
    deployment.apps/kf-api created

    (venv) you@you % kubectl apply -f autoscale.yaml 
    horizontalpodautoscaler.autoscaling/kf-api-hpa created

    (venv) you@you %  kubectl port-forward service/kf-api-svc 8080
    Forwarding from 127.0.0.1:8080 -> 8080
    Forwarding from [::1]:8080 -> 8080
    Handling connection for 8080

or:

    kubectl autoscale deployment kf-api --cpu-percent=50 --min=1 --max=10

like this:

    (venv) you@you % kubectl autoscale deployment kf-api --cpu-percent=50 --min=1 --max=10
    horizontalpodautoscaler.autoscaling/kf-api autoscaled

Check the current status of autoscaler

    (venv) you@you % kubectl get hpa
    NAME         REFERENCE           TARGETS         MINPODS   MAXPODS   REPLICAS   AGE
    kf-api-hpa   Deployment/kf-api   1%/50%          1         10        1          10h

    (venv) you@you % kubectl get hpa kf-api --watch    
    NAME     REFERENCE           TARGETS   MINPODS   MAXPODS   REPLICAS   AGE
    kf-api   Deployment/kf-api   2%/50%    1         10        1          113s


For continuous monitoring

    (venv) you@you % kubectl get hpa -w

## Load testing with Locust

in a file called locustfile.py you progam the test you want to run

```python
from locust import HttpUser, task

class LoadTesting(HttpUser):
    @task
    def hello_world(self):
        self.client.post("/api/v1/hello", json={})
```

Use `locust` to simulate a high load on the API

    pip install locust
    locust
    (k8_env) you@you % locust
    [2023-04-27 18:51:08,066] ..../INFO/locust.main: Starting web interface at http://0.0.0.0:8089 (accepting connections from all network interfaces)

this will deploy the browser interface to http://0.0.0.0:8089 

to test the endpoint http://0.0.0.0:8080/api/v1/hello/ 

enter http://0.0.0.0:8080 into the Host input field 

![Test drive the API](./resources/locustboard.png)

![Load testing with Locust](./resources/locust.png)

As Locust swarms your endpoint, you should see the usage go up on your horizontal pod scaler

    (venv) you@you % kubectl get hpa kf-api --watch    
    NAME     REFERENCE           TARGETS   MINPODS   MAXPODS   REPLICAS   AGE
    kf-api   Deployment/kf-api   2%/50%    1         10        1          113s
    kf-api   Deployment/kf-api   22%/50%   1         10        1          2m45s
    kf-api   Deployment/kf-api   323%/50%   1         10        1          3m45s
    kf-api   Deployment/kf-api   323%/50%   1         10        4          4m
    kf-api   Deployment/kf-api   323%/50%   1         10        7          4m15s
    kf-api   Deployment/kf-api   308%/50%   1         10        7          4m45s

you should see what if the TARGETS ration goes abive 50%:50%, more REPLICAS are spun up

## Teardown Kubernetes

    kubectl delete deployment kf-api
    kubectl delete svc kf-api-svc
    kubectl delete hpa kf-api-hpa

## Acknowledgements

Inspiration and code for FastAPI setup:
[How to continuously deploy a fastAPI to AWS Lambda with AWS SAM](https://iwpnd.pw/articles/2020-01/deploy-fastapi-to-aws-lambda).

## helpful links 

https://www.linuxsysadmins.com/service-unavailable-kubernetes-metrics/

https://stackoverflow.com/questions/54106725/docker-kubernetes-mac-autoscaler-unable-to-find-metrics 


## helpful snippets


