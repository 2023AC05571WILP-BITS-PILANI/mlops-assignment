#!/bin/bash

# Create directories for Prometheus config
mkdir -p prometheus_data
mkdir -p prometheus_config

# Create Prometheus config file
cat <<EOF > prometheus_config/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'local-metrics'
    static_configs:
      - targets: ['host.docker.internal:8000']
EOF

# Run Prometheus container
docker run -d \
  -p 9090:9090 \
  -v "$(pwd)/prometheus_config/prometheus.yml:/etc/prometheus/prometheus.yml" \
  -v "$(pwd)/prometheus_data:/prometheus" \
  prom/prometheus

# Run Grafana container
docker run -d \
  -p 3000:3000 \
  grafana/grafana

echo "✅ Prometheus is running at http://localhost:9090"
echo "✅ Grafana is running at http://localhost:3000"
echo "👉 Login to Grafana (default: admin/admin), add Prometheus as a data source (http://host.docker.internal:9090)"
