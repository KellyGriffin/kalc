echo "Pods before running daemonset:"
kubectl get pods
kubectl apply -f ../incomming_change.yaml
sleep 10
echo "Pods after  running daemonset:"
kubectl get pods
sleep 10
echo "Pods after 20 seconds since running daemonset:"
kubectl get pods