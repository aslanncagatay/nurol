NUROL IOT PROJECT

## Modules

| Module | Stack | Purpose |
| --- | --- | --- |
| `service-registry` | Spring Cloud Eureka | Service discovery |
| `config-server` | Spring Cloud Config | Centralised configuration |
| `api-gateway` | Spring Cloud Gateway | Single entry point, port 8060 |
| `employee-service` / `department-service` | Spring Boot | Domain services |
| `sender-service` / `receiver-service` | Spring Boot + RabbitMQ | Message ingress and egress |
| `iot-agent` | Python + LangGraph | Telemetry triage state machine ([docs](iot-agent/README.md)) |
| `front-end` | — | UI |
| `k8s` | Kubernetes | Deployment manifests |
