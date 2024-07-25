#!/bin/bash

SCRIPTS_DIR=/root/cis-scripts
TIME_1=10
TIME_2=2
TIME_3=10

echo "[$(date)] start..."
for i in {1..20}
do
  echo "[$(date)] time $i"
  kubectl apply -f $SCRIPTS_DIR/301/cm-150.yaml
  sleep $TIME_1
  kubectl apply -f $SCRIPTS_DIR/301/cm-200.yaml
  sleep $TIME_1
  echo "[$(date)] 10 app upgrade"
  for j in 1 3 5 7 8 9 12 13 14 15
  do
    kubectl delete deploy app-svc-5-app -n bigip-ctlr-ns-$j
    sleep $TIME_2
  done
  kubectl apply -f $SCRIPTS_DIR/301/app-200.yaml
  sleep $TIME_3
  echo "[$(date)] 10 app sacle up"
  for k in 2 4 6 8 9 10 11 16 17 18
  do
    kubectl scale deploy app-svc-8-app -n bigip-ctlr-ns-$k --replicas=2
    sleep $TIME_2
  done
  sleep $TIME_3
  echo "[$(date)] 10 app sacle down"
  for l in 2 4 6 8 9 10 11 16 17 18
  do
    kubectl scale deploy app-svc-8-app -n bigip-ctlr-ns-$l --replicas=1
    sleep $TIME_2
  done
  sleep $TIME_3
done
echo "[$(date)] end"
