# Custom metrics in Python with OpenTelemetry (and Prometheus)
The original video guide is from [Google Cloud Tech - Custom metrics with OpenTelemetry](https://www.youtube.com/watch?v=OHJKH2-w8OY&list=PLIivdWyY5sqLuKKx4pcdEAkJY1HevjVVm&index=16), the code from this repository is modified from [stack-doctor](https://github.com/yuriatgoogle/stack-doctor/tree/otel-metrics/opentelemetry-metrics-demo/python). 

This guide enhance the original guide by introducing detail steps as well as modifications about the default behavior. The demo application is written in Pythona and OpenTelemetry Collector will collect the metrics and transport to Cloud Logging.

## The app and instrumentation
The code is availiable under my [repo](https://github.com/tbd).  


### Metric definition
```python
  requests_counter = meter.create_counter("otel_total_requests_custom")
  errors_counter = meter.create_counter("otel_failed_requests_custom")
  request_latency = meter.create_histogram("otel_request_latency_custom")
```


### Request handling
```python
  @app.route('/')
  def index():
      requests_counter.add(1)
      start = time.time()
      sleep(randint(1,1000)/1000)
      latency = time.time() - start
      if randint(1,100) > 95:
          # fail 5 % of the time
          errors_counter.add(1)
          request_latency.record(latency)
          return 'Processing failed!', 500
      request_latency.record(latency)
      return 'returned in ' + str(round(latency, 3) * 1000) + ' ms', 200
```


# Deploying the app
To deploy the applicaiton, the following resources is resuired
* Creating a GKE cluster
* GCP IAM permissions
* GCP APIs

## Creating the cluster


```bash

```

```bash
$ kubectl get nodes
NAME                                     STATUS   ROLES    AGE     VERSION
gke-small-cluster-pool-1-b40da891-fc1p   Ready    <none>   7h27m   v1.15.7-gke.23
```


## Build Docker Images
Create Dockerfile:
```Dockerfile
# start by pulling the python image
FROM python:3.9.12

# copy the requirements file into the image
COPY ./requirements.txt /app/requirements.txt

# switch working directory
WORKDIR /app

# install the dependencies and packages in the requirements file
RUN pip install -r requirements.txt

# copy every content from the local file to the image
COPY . /app

# configure the container to run in an executed manner
ENTRYPOINT [ "python" ]

CMD ["app.py"]
```



## Deploy Config Map
kubectl apply -f collector-config-map.yaml

## Deploy OpenTelemetry Collecotr
kubectl apply -f collector-gke.yaml

Refer Google Cloud Exporter [Configuration References](https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/main/exporter/googlecloudexporter/README.md) to configure optional settings.

Configure resource type detection
```yaml
    resourcedetection:
      detectors: [gcp]
      timeout: 10s
```

## Get collector IP 
kubectl get pods -o wide

Update the Collecotr's IP in the app.py file.

## Build Container 

```shell
docker build -t otel-metrics:0.7 .
```

Tag docker image

```shell
docker tag otel-metrics:0.7 gcr.io/sandbox-project-379303/otel-metrics:0.7
```

Push docker image to GCP container registry
```shell
docker push gcr.io/sandbox-project-379303/otel-metrics:0.7
```

## Deploy application
kubectl apply -f deployment.yaml to create the app and `kubectl expose deployment --type=LoadBalancer` to make it externally available. 


## Deploy traffic.yaml
kubectl apply -f traffic.yaml

Wait for few mimutes and search relevant metricss in Cloud Monitoring.