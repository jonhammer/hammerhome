for i in `ls | grep yaml`; do kubectl cp `kubectl get pods | grep home-assistant | awk '{print $1}'`:/config/$i $i; done
kubectl cp `kubectl get pods | grep home-assistant | awk '{print $1}'`:/config/packages/. /home/jon/hammernet/home_assistant/has_config/packages/
kubectl cp `kubectl get pods | grep home-assistant | awk '{print $1}'`:/config/python_scripts/. /home/jon/hammernet/home_assistant/has_config/python_scripts/
