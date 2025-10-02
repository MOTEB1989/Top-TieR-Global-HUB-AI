# Observability Stack

This compose bundle provisions Prometheus, Grafana, and an OpenSearch logging pipeline tailored for the Top-TieR Global HUB AI platform.

## Services

| Service | Description | Default Port |
|---------|-------------|--------------|
| Prometheus | Metrics scraping and storage | 9090 |
| Grafana | Dashboard visualisation | 3001 |
| OpenSearch | Centralised log storage | 9200 |
| OpenSearch Dashboards | Log exploration UI | 5601 |
| Fluent Bit | Log forwarder into OpenSearch | n/a |

## Usage

```bash
cd monitoring
docker compose up -d
```

Once started, Grafana will ship with pre-provisioned dashboards and datasources. Default credentials can be overridden using `GRAFANA_ADMIN_USER` and `GRAFANA_ADMIN_PASSWORD` environment variables.

Prometheus scrapes all FastAPI services via `/metrics`, which are automatically exposed through the API server instrumentation. Configure gateway, runner, and dashboard services to expose Prometheus metrics on the same endpoint for full coverage.
