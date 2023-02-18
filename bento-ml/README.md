# Bento ML

BentoML is an open source framework for high performance ML model serving.

## Table of Contents

* [YOLO v5](#yolov5)
    * [Running Instructions](#running-instructions)
    * [Building and Deploying BentoML Service to Docker](#building-and-deploying-bentoml-service-to-docker)

## YOLOv5

### Running Instructions

1. Prepare the model

```bash
$ cd yolov5
$ python bento_ml.py
```

2. Run the BentoML service

```bash
$ bentoml serve service.py:svc
```

3. Send a request to the service

```bash
$ curl -X POST -H "Content-Type: text/plain" --data 'SAMPLE IMG URI' http://localhost:3000/predict
```

### Building and Deploying BentoML Service to Docker

Before building the docker image, make sure you have the pretrained model in the correct directory.
Also, make sure you have the `bentoml` cli installed, and the `bentofile.yaml` is in the same directory as the `service.py` file.

```bash
$ bentoml build
```

Once the build is successful, you will get an output as follows:

```
Successfully built Bento(tag="pytorch_yolo_demo:dczcz4fppglvaiva").
```

Then, you can run the docker image with the following command:

```bash
bentoml containerize pytorch_yolo_demo:dczcz4fppglvaiva

# > Successfully built docker image "pytorch_yolo_demo:dczcz4fppglvaiva"

docker run --gpus all -p 3000:3000 pytorch_yolo_demo:dczcz4fppglvaiva
```
