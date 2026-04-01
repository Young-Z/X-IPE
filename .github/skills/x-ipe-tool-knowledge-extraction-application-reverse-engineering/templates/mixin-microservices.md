# Application RE — Microservices Mixin

> Apply this mixin when the target codebase contains multiple independently deployable services.
> Merge these into the base playbook and collection templates when mixin_key: microservices.

---

## Detection Signals

| Signal | File/Pattern | Confidence |
|--------|-------------|------------|
| Docker Compose | `docker-compose.yml` with multiple services | high |
| Multiple Dockerfiles | `*/Dockerfile` in multiple directories | high |
| K8s manifests | `deployment.yaml`, `service.yaml`, `ingress.yaml` | high |
| API gateway config | `kong.yml`, `nginx.conf` with upstream blocks, `envoy.yaml` | medium |
| Service mesh | `istio` configs, `linkerd` annotations | medium |
| Multiple go.mod/package.json | Independent `go.mod` or `package.json` per service directory | medium |
| Proto/gRPC files | `*.proto` files with service definitions | medium |

---

## Additional Sections

### Service Landscape View

Add to Section 1 (Architecture Recovery):
- Architecture DSL landscape view showing all services and their communication
- Document each service's responsibility and bounded context
- Identify shared infrastructure (databases, message brokers, caches)

### Inter-Service Communication

Add to Section 6 (Data Flow / Protocol Analysis):
- Document all communication protocols between services (REST, gRPC, message queues)
- Map synchronous vs. asynchronous communication patterns
- Identify service mesh / API gateway routing rules
- Document retry/timeout/circuit breaker patterns

---

## Section Overlay Prompts

### For Section 1 (Architecture Recovery)
<!-- ADDITIONAL PROMPTS:
- Create service landscape using Architecture DSL showing all services
- For each service: create internal module view
- Document service boundaries and bounded contexts
- Identify shared databases vs. per-service databases
- Map API gateway routing to backend services
-->

### For Section 3 (API Contracts)
<!-- ADDITIONAL PROMPTS:
- Document inter-service API contracts (service A calls service B)
- Extract protobuf/gRPC service definitions if present
- Document message queue schemas (event payloads)
- Identify API versioning strategy across services
-->

### For Section 4 (Dependency Analysis)
<!-- ADDITIONAL PROMPTS:
- Map service-to-service runtime dependencies
- Identify shared libraries/packages across services
- Document infrastructure dependencies (databases, message brokers, caches)
- Identify deployment order constraints
-->

### For Section 6 (Data Flow)
<!-- ADDITIONAL PROMPTS:
- Trace cross-service request flows end-to-end
- Document async event flows (pub/sub, message queues)
- Identify saga/orchestration patterns for distributed transactions
- Map data consistency patterns (eventual vs. strong)
-->

### For Section 8 (Source Code Tests)
<!-- ADDITIONAL PROMPTS:
- Identify per-service test suites
- Note contract tests between services (e.g., Pact)
- Check for end-to-end tests that span services
- Identify test doubles for external service calls
-->
