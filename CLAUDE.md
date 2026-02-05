# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a hands-on Platform Engineering Architect course repository containing workshop modules for building a complete Kubernetes-based engineering platform. The course teaches platform concepts through practical exercises covering monitoring, policy management, security operations, and team management capabilities.

## High-Level Architecture

The repository is structured as a workshop with progressive learning modules:

1. **Foundation**: Base Kubernetes setup with Grafana monitoring stack (Prometheus, Grafana, AlertManager) and OPA Gatekeeper policy engine
2. **CapOc (Compliance at Point of Change)**: CVE scanning and code quality policy enforcement using Gatekeeper constraint templates
3. **SecOps**: Runtime security monitoring with Falco and security policy constraints
4. **Teams Management**: Full-stack platform application with:
   - FastAPI-based Teams API (Python, in-memory storage)
   - CLI tool (Python Click framework)
   - Angular web UI with Nginx
   - Custom Kubernetes operator that watches the Teams API and manages team namespaces

All components are designed to run in Kubernetes with coder.com remote development environments as the primary development platform.

## Common Development Commands

### Foundation Module Setup

```bash
# Add Helm repositories
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add falcosecurity https://falcosecurity.github.io/charts
helm repo update

# Install Grafana monitoring stack
helm install grafana-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --values grafana-stack-values.yaml \
  --wait

# Install Gatekeeper
kubectl apply -f https://raw.githubusercontent.com/open-policy-agent/gatekeeper/release-3.14/deploy/gatekeeper.yaml
kubectl wait --for=condition=Ready pod -l control-plane=controller-manager -n gatekeeper-system --timeout=90s

# Access Grafana (with coder desktop installed)
kubectl port-forward -n monitoring service/grafana-stack 3000:80
# Then access: http://<workspace-name>.coder:3000/grafana
# Default credentials: admin/admin123
```

### Gatekeeper Policy Management

```bash
# Apply constraint templates and constraints
kubectl apply -f <constraint-template-file>.yaml
kubectl apply -f <constraint-file>.yaml

# Verify policies
kubectl get constrainttemplates
kubectl get constraints
kubectl describe constraint <constraint-name>

# Test policy enforcement
kubectl create namespace test-namespace  # Should fail if required labels missing
kubectl apply -f deployment.yaml  # Will be validated against active constraints
```

### SecOps Module

```bash
# Install Falco runtime security
helm install falco falcosecurity/falco \
  --namespace falco-system \
  --create-namespace \
  --set driver.kind=modern_ebpf \
  --set falco.grpc.enabled=true \
  --set falco.grpcOutput.enabled=true

# Check Falco logs for security alerts
kubectl logs -n falco-system daemonset/falco | tail -20
kubectl logs -n falco-system daemonset/falco | grep "Privileged container"

# Deploy custom security rules
helm upgrade falco falcosecurity/falco \
  --namespace falco-system \
  --set-file customRules."custom_rules\.yaml"=./root-detect-rule.yaml
```

### Teams API (FastAPI)

```bash
# Deploy Teams API
kubectl create namespace teams-api
kubectl apply -f workshop/teams-management/teams-api/k8s/

# Verify deployment
kubectl get pods -n teams-api
kubectl get svc -n teams-api

# Port forward for local access
kubectl port-forward -n teams-api svc/teams-api-service 8080:4200
# Access API: http://<workspace-name>.coder:3002

# Health check
curl http://<workspace-name>.coder:3002/health

# API operations
curl http://localhost:8080/teams
curl -X POST "http://localhost:8080/teams" -H "Content-Type: application/json" -d '{"name": "Backend Team"}'
curl -X DELETE http://localhost:8080/teams/<team-id>

# Access interactive docs
# http://localhost:8080/docs
```

### Teams CLI Tool

```bash
cd workshop/teams-management/cli

# Install dependencies
pip install -r requirements.txt

# Make CLI executable
chmod +x teams_cli.py

# Use CLI commands
python teams_cli.py health
python teams_cli.py list
python teams_cli.py create "Team Name"
python teams_cli.py get <team-id>
python teams_cli.py delete <team-id>
```

### Teams Web UI (Angular)

```bash
cd workshop/teams-management/teams-app

# Deploy to Kubernetes
kubectl apply -f k8s/

# Port forward for local access
kubectl port-forward -n engineering-platform svc/teams-ui-service 4200:80

# Local development (if needed)
npm install
ng serve
```

### Teams Operator (Kubernetes Controller)

```bash
cd workshop/teams-management/teams-operator

# Deploy operator
kubectl apply -f operator-deployment.yaml

# Check operator logs
kubectl logs -n teams-api deployment/teams-operator -f
```

## Key Technical Details

### Port Forwarding with Coder Desktop

The workshop is designed for coder.com environments. To access port-forwarded services:
1. Install coder desktop: `brew install --cask coder/coder/coder-desktop`
2. Connect via SSH: `ssh <workspace-name>.coder`
3. Access services at: `http://<workspace-name>.coder:<port>`

### Gatekeeper Constraint Template Pattern

Constraint templates use Rego policy language and follow this structure:
- ConstraintTemplate: Defines the CRD and Rego validation logic
- Constraint: Instantiates the template with specific parameters and target resources

Example flow:
1. Create ConstraintTemplate (defines validation logic)
2. Apply Constraint (applies template with parameters)
3. Kubernetes admission controller validates resources against constraints
4. Non-compliant resources are rejected with detailed error messages

### Teams API Architecture

The Teams API uses in-memory storage (teams_store dict in main.py), meaning:
- Data is lost on pod restart (not production-ready without database)
- No persistence layer implemented
- Perfect for workshop/learning environment
- FastAPI with CORS enabled for UI integration
- Health endpoint at `/health` for Kubernetes probes

### Teams Operator Behavior

The custom Kubernetes operator (teams_operator.py):
- Watches the Teams API for team creation/deletion events
- Automatically creates/destroys corresponding Kubernetes namespaces
- Provides platform self-service capability
- Demonstrates platform automation patterns

## Important Conventions

### Namespace Organization

- `monitoring`: Grafana stack and monitoring tools
- `gatekeeper-system`: OPA Gatekeeper components
- `falco-system`: Falco runtime security
- `teams-api`: Teams API service
- `engineering-platform`: Teams web UI and related services

### Container Images

Pre-built images available on Docker Hub:
- `olivercodes01/teams-api:latest` - Teams API service
- Other services use standard public images (nginx, busybox, etc.)

### Policy Naming

Constraint templates and constraints follow lowercase naming:
- Constraint template: `k8srequiredlabels`
- Constraint kind: `K8sRequiredLabels` (CamelCase)
- Constraint instance: `ns-must-have-gk` (kebab-case)

### Team Naming Recommendations

When creating teams via API/CLI/UI, avoid spaces in team names for better compatibility:
- Use: `BackendTeam`, `Backend-Team`, or `backend_team`
- Avoid: `Backend Team` (spaces can cause issues)

## Monitoring and Observability

### Grafana Dashboards

Access Grafana at `http://<workspace-name>.coder:3000/grafana` to view:
- Kubernetes / Compute Resources / Namespace (Pods)
- Select specific namespace to see metrics
- Pre-configured dashboards for cluster monitoring

### Falco Security Alerts

Monitor Falco for runtime security events:
```bash
kubectl logs -n falco-system daemonset/falco -f
```

Common alert patterns:
- Privileged container executions
- Root user activities in containers
- Suspicious network connections
- File access violations

## Module Completion Order

The recommended workshop path:
1. **Foundation** (Required first) - Sets up Kubernetes, Grafana, Gatekeeper
2. **CapOc** (Recommended second) - CVE and quality policy enforcement
3. **SecOps** (Can be done in any order) - Runtime security monitoring
4. **Teams Management** (Final module) - Complete platform application

Each module builds on Foundation concepts but CapOc/SecOps are independent of each other.

## Troubleshooting Patterns

### Pod Not Starting

```bash
kubectl describe pod <pod-name> -n <namespace>
kubectl logs <pod-name> -n <namespace>
kubectl top nodes  # Check resource availability
```

### Gatekeeper Not Enforcing Policies

```bash
kubectl get pods -n gatekeeper-system
kubectl get constrainttemplates
kubectl get constraints
kubectl describe constraint <constraint-name>
kubectl rollout restart deployment -n gatekeeper-system gatekeeper-controller-manager
```

### API Connection Issues

```bash
# Verify service exists
kubectl get svc -n <namespace>
kubectl get endpoints -n <namespace>

# Check port forwarding
lsof -i :<port>

# Restart port forward
kubectl port-forward -n <namespace> svc/<service-name> <local-port>:<service-port>
```

### Resource Constraints

```bash
kubectl top nodes
kubectl top pods --all-namespaces

# Scale down if needed
kubectl scale deployment <deployment-name> --replicas=1 -n <namespace>
```

## Development Notes

- The repository uses standard Kubernetes YAML manifests (no Kustomize or Helm charts for workshop components)
- FastAPI automatically generates OpenAPI docs at `/docs` and `/redoc` endpoints
- Angular app uses proxy configuration for API calls (proxy.conf.json)
- Constraint templates use Rego language (similar to Datalog)
- All workshop resources use minimal resource requests/limits for development environments
