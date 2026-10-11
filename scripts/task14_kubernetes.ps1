docker build -f api\Dockerfile -t task14-cifar-api:v1 .
docker build -f ui\Dockerfile -t task14-cifar-ui:v1 .

minikube start --driver=docker --cpus=4 --memory=6144
minikube addons enable metrics-server
minikube image load task14-cifar-api:v1
minikube image load task14-cifar-ui:v1

kubectl apply -f k8s\namespace.yaml
kubectl apply -f k8s\api-deployment.yaml
kubectl apply -f k8s\api-service.yaml
kubectl apply -f k8s\ui-deployment.yaml
kubectl apply -f k8s\ui-service.yaml

kubectl scale deployment/cifar-api --replicas=3 -n task14
kubectl scale deployment/cifar-ui --replicas=3 -n task14

kubectl rollout status deployment/cifar-api -n task14
kubectl rollout status deployment/cifar-ui -n task14

kubectl get all -n task14
kubectl get pods -n task14 -o wide
kubectl get rs -n task14
kubectl top nodes
kubectl top pods -n task14

docker build -f api\Dockerfile -t task14-cifar-api:v2 .
minikube image load task14-cifar-api:v2
kubectl set image deployment/cifar-api cifar-api=task14-cifar-api:v2 -n task14
kubectl set env deployment/cifar-api APP_VERSION=v2 -n task14
kubectl rollout status deployment/cifar-api -n task14
kubectl rollout history deployment/cifar-api -n task14

kubectl exec -n task14 deployment/cifar-ui -- python -c "import urllib.request; print(urllib.request.urlopen('http://cifar-api:5000/health').read().decode())"

minikube service cifar-ui -n task14
