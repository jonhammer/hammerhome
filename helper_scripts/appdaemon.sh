#!/bin/bash
# kubectl cp /home/jon/repos/home/lib/app_daemon/conf/apps/lights.py `kubectl get pods | grep appdaemon | awk '{print $1}'`:/conf/apps/lights.py
kubectl cp /home/jon/repos/home/lib/data/home.yaml `kubectl get pods | grep appdaemon | awk '{print $1}'`:/conf/apps/home.yaml
