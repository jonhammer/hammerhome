# Alerts
This folder contains [TICKScript](https://docs.influxdata.com/kapacitor/v1.6/tick/) alerts (used in conjuction with [InfluxDB](https://www.influxdata.com/time-series-platform/influxdb/) and [Kapacitor](https://www.influxdata.com/time-series-platform/kapacitor/)). This will be deprecated in the future in favor of the Flux language.

These alerts are intended detect when IOT devices go offline for extended periods of time. The alerts are saved to a new measurement in Influx that are visualized in Grafana.

In order to use these alerts, you need to first [send your home assistant data to an influxdb instance](https://www.home-assistant.io/integrations/influxdb/).