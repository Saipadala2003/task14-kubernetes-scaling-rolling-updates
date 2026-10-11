# Task 14 - Kubernetes Scaling and Rolling Updates

## Objective
Implement scalability and deployment update strategies using Kubernetes.

## Deep Learning Application
A fresh **PyTorch CIFAR-10 CNN** image classification application is used for Task 14. It is independent of the Task 13 TensorFlow MNIST application.

### CIFAR-10 classes
airplane, automobile, bird, cat, deer, dog, frog, horse, ship, truck

## Architecture

```text
Browser
   |
   v
Streamlit UI
NodePort :30082
   |
   v
Flask CNN API
ClusterIP :5000
   |
   v
PyTorch CIFAR-10 CNN
```

## Project structure

```text
.
├── api/
│   ├── app.py
│   ├── model_def.py
│   ├── Dockerfile
│   └── requirements.txt
├── ui/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── k8s/
│   ├── namespace.yaml
│   ├── api-deployment.yaml
│   ├── api-service.yaml
│   ├── ui-deployment.yaml
│   └── ui-service.yaml
├── scripts/
│   ├── windows_setup.ps1
│   └── task14_kubernetes.ps1
├── train_model.py
├── screenshots/
│   └── README.txt
└── reports/
    └── README.md
```

## 1. Windows setup

Use a short project path such as:

```text
C:\T14
```

Create and activate the environment:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r api\requirements.txt
```

## 2. Train the model

```powershell
python train_model.py --epochs 5 --batch-size 128
```

The model is saved to:

```text
model/cifar10_cnn.pth
```

The model binary is intentionally not stored in GitHub. Generate it locally before building the Docker API image.

## 3. Build Docker images

```powershell
docker build -f api\Dockerfile -t task14-cifar-api:v1 .
docker build -f ui\Dockerfile -t task14-cifar-ui:v1 .
```

## 4. Start Minikube

```powershell
minikube start --driver=docker --cpus=4 --memory=6144
minikube addons enable metrics-server
```

Load local images:

```powershell
minikube image load task14-cifar-api:v1
minikube image load task14-cifar-ui:v1
```

## 5. Deploy

```powershell
kubectl apply -f k8s\namespace.yaml
kubectl apply -f k8s\api-deployment.yaml
kubectl apply -f k8s\api-service.yaml
kubectl apply -f k8s\ui-deployment.yaml
kubectl apply -f k8s\ui-service.yaml
```

Verify:

```powershell
kubectl get all -n task14
kubectl get pods -n task14 -o wide
```

## 6. Scale replicas

Scale the Flask API to three replicas:

```powershell
kubectl scale deployment/cifar-api --replicas=3 -n task14
kubectl rollout status deployment/cifar-api -n task14
```

Scale the Streamlit UI to three replicas:

```powershell
kubectl scale deployment/cifar-ui --replicas=3 -n task14
kubectl rollout status deployment/cifar-ui -n task14
```

Verify:

```powershell
kubectl get pods -n task14 -o wide
kubectl get deployments -n task14
```

## 7. Rolling update

Build a second API image:

```powershell
docker build -f api\Dockerfile -t task14-cifar-api:v2 .
minikube image load task14-cifar-api:v2
```

Perform the rolling update:

```powershell
kubectl set image deployment/cifar-api cifar-api=task14-cifar-api:v2 -n task14
kubectl set env deployment/cifar-api APP_VERSION=v2 -n task14
kubectl rollout status deployment/cifar-api -n task14
```

Monitor:

```powershell
kubectl get pods -n task14 -w
kubectl get rs -n task14
kubectl rollout history deployment/cifar-api -n task14
```

## 8. Resource monitoring

```powershell
kubectl top nodes
kubectl top pods -n task14
```

## 9. Health validation

```powershell
kubectl exec -n task14 deployment/cifar-ui -- python -c "import urllib.request; print(urllib.request.urlopen('http://cifar-api:5000/health').read().decode())"
```

Expected structure:

```json
{"model_loaded":true,"status":"healthy","success":true,"version":"v2"}
```

## 10. Open the application

```powershell
minikube service cifar-ui -n task14
```

Upload a color image and verify the CIFAR-10 prediction.

## Evidence
The Task 14 report/screenshots should document:
- Minikube status
- Kubernetes node
- Initial deployment
- Scale-out to three replicas
- ReplicaSet history
- Rolling update status
- CPU and memory utilization
- Health endpoint
- Browser availability
- Image classification result

## Submission
Submit the public GitHub repository together with the Task 14 PDF through the L&T Edutech LMS.
