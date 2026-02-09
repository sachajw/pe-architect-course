# Foundation Workshop - Monitoring and Policy Management

## Purpose

This workshop establishes the foundational infrastructure for the Kubernetes platform, deploying essential monitoring (Grafana Stack) and policy enforcement (Gatekeeper) components using GitOps principles with FluxCD.

## Overview

**Deployed Components:**
- **Grafana Stack** - Complete monitoring solution (Prometheus + Grafana + AlertManager)
- **Gatekeeper** - OPA-based policy enforcement for Kubernetes admission control

**Deployment Method:** GitOps via FluxCD  
**Namespaces:**
- `monitoring` - Grafana Stack components
- `gatekeeper-system` - Gatekeeper components

## Architecture

```
?????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
???  Foundation Workshop Infrastructure                     ???
?????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
???                                                         ???
???  ????????????????????????????????????????????????????????????????????????  ???????????????????????????????????????????????????????????????????????????  ???
???  ???  Monitoring          ???  ???  Policy Enforcement   ???  ???
???  ???  Namespace           ???  ???  Namespace            ???  ???
???  ????????????????????????????????????????????????????????????????????????  ???????????????????????????????????????????????????????????????????????????  ???
???  ??? ??? Prometheus         ???  ??? ??? Gatekeeper          ???  ???
???  ??? ??? Grafana            ???  ???   Controller          ???  ???
???  ??? ??? AlertManager       ???  ??? ??? Gatekeeper Audit    ???  ???
???  ??? ??? Node Exporter      ???  ???                       ???  ???
???  ??? ??? Kube State Metrics ???  ???                       ???  ???
???  ????????????????????????????????????????????????????????????????????????  ???????????????????????????????????????????????????????????????????????????  ???
???                                                         ???
?????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
```

## Components

### Grafana Stack (kube-prometheus-stack)

Complete monitoring stack including:

**Prometheus:**
- Time-series database for metrics
- Resource limits: 1Gi/500m (requests), 2Gi/1000m (limits)
- 7-day retention period
- 10Gi storage volume

**Grafana:**
- Visualization and dashboards
- Resource limits: 256Mi/100m (requests), 512Mi/500m (limits)
- NodePort service on port 30300
- 2Gi persistent storage
- Default credentials: admin/admin123

**AlertManager:**
- Alert aggregation and routing
- Resource limits: 128Mi/100m (requests), 256Mi/200m (limits)

**Exporters:**
- Node Exporter - Host-level metrics
- Kube State Metrics - Kubernetes resource metrics

**Disabled Components** (to conserve resources):
- kube-etcd monitoring
- kube-controller-manager monitoring
- kube-scheduler monitoring

### Gatekeeper (OPA)

Policy enforcement using Open Policy Agent:

**Components:**
- Gatekeeper Controller Manager - Admission webhook
- Gatekeeper Audit - Periodic policy auditing

**Configuration:**
- Single replica for each component (suitable for dev/test)
- CRDs for ConstraintTemplates and Constraints

## Repository Structure

```
workshop/foundation/
????????? README.md                           # Original workshop instructions
????????? flux-resources/                     # GitOps manifests
???   ????????? namespace.yaml                  # monitoring namespace
???   ????????? helmrepository.yaml             # Helm repo definitions
???   ????????? grafana-stack-configmap.yaml    # Grafana values
???   ????????? grafana-stack-helmrelease.yaml  # Grafana HelmRelease
???   ????????? gatekeeper-helmrelease.yaml     # Gatekeeper HelmRelease
???   ????????? kustomization.yaml              # Kustomize bundle
????????? grafana-stack-values.yaml           # Helm values (reference)
????????? simple-constraint-template.yaml     # Example Gatekeeper template
????????? simple-constraint.yaml              # Example Gatekeeper constraint
????????? simple-ns-with-label.yaml          # Test namespace

fluxcd/cluster/kind-5min-idp/
????????? workshop-foundation.yaml            # Flux Kustomization
```

## Deployment

### Prerequisites

- FluxCD installed and configured
- GitHub deploy key configured
- kubectl access to cluster

### GitOps Deployment

The foundation workshop is deployed automatically via FluxCD:

1. **Flux Kustomization** (`workshop-foundation`) monitors:
   - Path: `./workshop/foundation/flux-resources`
   - Interval: 5 minutes
   - Wait: enabled (waits for resources to be ready)
   - Prune: enabled (removes deleted resources)

2. **HelmRepositories** defined in flux-system:
   - `prometheus-community` - https://prometheus-community.github.io/helm-charts
   - `gatekeeper` - https://open-policy-agent.github.io/gatekeeper/charts

3. **HelmReleases** deployed:
   - `grafana-stack` (monitoring namespace) - kube-prometheus-stack v81.5.0+
   - `gatekeeper` (gatekeeper-system namespace) - gatekeeper v3.15.0+

### Manual Deployment (Alternative)

If not using GitOps:

```bash
# Apply all resources
kubectl apply -k workshop/foundation/flux-resources/

# Or manually install with Helm
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add gatekeeper https://open-policy-agent.github.io/gatekeeper/charts
helm repo update

kubectl create namespace monitoring
helm install grafana-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --values workshop/foundation/grafana-stack-values.yaml

kubectl create namespace gatekeeper-system
helm install gatekeeper gatekeeper/gatekeeper \
  --namespace gatekeeper-system
```

## Verification

### Check Deployment Status

```bash
# Check Flux Kustomization
flux get kustomizations workshop-foundation

# Check HelmReleases
flux get helmreleases -A

# Check pods
kubectl get pods -n monitoring
kubectl get pods -n gatekeeper-system

# Check services
kubectl get svc -n monitoring
```

### Expected Output

**Flux Status:**
```
NAME                REVISION           SUSPENDED  READY  MESSAGE
workshop-foundation main@sha1:beccfe7c False      True   Applied revision: main@sha1:beccfe7c
```

**HelmReleases:**
```
NAMESPACE           NAME           REVISION  SUSPENDED  READY  MESSAGE
gatekeeper-system   gatekeeper     3.21.1    False      True   Helm install succeeded
monitoring          grafana-stack  81.5.0    False      True   Helm install succeeded
```

**Monitoring Pods:**
```
NAME                                                     READY   STATUS
alertmanager-grafana-stack-kube-prometh-alertmanager-0   2/2     Running
grafana-stack-bb649f97b-xxxxx                            3/3     Running
grafana-stack-kube-prometh-operator-574759cb46-xxxxx     1/1     Running
grafana-stack-kube-state-metrics-6875658577-xxxxx        1/1     Running
grafana-stack-prometheus-node-exporter-xxxxx             1/1     Running
prometheus-grafana-stack-kube-prometh-prometheus-0       2/2     Running
```

**Gatekeeper Pods:**
```
NAME                                             READY   STATUS
gatekeeper-audit-9c777fbb7-xxxxx                 1/1     Running
gatekeeper-controller-manager-588bd8976b-xxxxx   1/1     Running
```

## Usage

### Accessing Grafana

**Shell Alias Method:**
```bash
# Start port-forward (alias configured in ~/.zshrc)
grafana-forward

# Access in browser: http://localhost:3000
# Username: admin
# Password: admin123
```

**Manual Port-Forward:**
```bash
kubectl port-forward -n monitoring svc/grafana-stack 3000:80
```

**NodePort Access** (if on same network):
```
http://<node-ip>:30300
```

### Grafana Initial Setup

1. Navigate to http://localhost:3000
2. Login with admin/admin123
3. Explore pre-configured dashboards:
   - Go to Dashboards ??? Browse
   - Key dashboards:
     - Kubernetes / Compute Resources / Cluster
     - Kubernetes / Compute Resources / Namespace (Pods)
     - Kubernetes / Compute Resources / Node (Pods)

### Using Gatekeeper

**Apply a ConstraintTemplate:**
```bash
kubectl apply -f workshop/foundation/simple-constraint-template.yaml
```

**Apply a Constraint:**
```bash
kubectl apply -f workshop/foundation/simple-constraint.yaml
```

**Test Constraint Enforcement:**
```bash
# This should fail (no required label)
kubectl create namespace test-fail

# This should succeed (has required label)
kubectl apply -f workshop/foundation/simple-ns-with-label.yaml
```

**Check Constraint Status:**
```bash
kubectl get constrainttemplates
kubectl get constraints
kubectl describe k8srequiredlabels ns-must-have-admission
```

## Configuration

### Modifying Grafana Stack Values

Values are stored in ConfigMap for GitOps workflow:

```bash
# Edit the ConfigMap
kubectl edit configmap grafana-stack-values -n monitoring

# Or update in Git
vim workshop/foundation/flux-resources/grafana-stack-configmap.yaml
git add . && git commit -m "Update Grafana config"
git push
```

Key configuration options:

**Prometheus:**
- `retention` - Data retention period (default: 7d)
- `storageSpec.volumeClaimTemplate.spec.resources.requests.storage` - Storage size
- `resources` - CPU/Memory limits

**Grafana:**
- `adminPassword` - Admin password
- `service.nodePort` - NodePort number
- `persistence.size` - Storage size

**AlertManager:**
- `enabled` - Enable/disable AlertManager
- `resources` - CPU/Memory limits

### Modifying Gatekeeper Configuration

Edit the HelmRelease:

```bash
# Edit in Git
vim workshop/foundation/flux-resources/gatekeeper-helmrelease.yaml

# Commit and push
git add . && git commit -m "Update Gatekeeper config"
git push
```

Configuration options:
- `replicas` - Number of controller replicas
- `audit.replicas` - Number of audit replicas
- `validatingWebhookConfiguration` - Webhook settings

## Troubleshooting

### Grafana Not Accessible

**Check pod status:**
```bash
kubectl get pods -n monitoring -l app.kubernetes.io/name=grafana
kubectl logs -n monitoring -l app.kubernetes.io/name=grafana
```

**Check service:**
```bash
kubectl get svc grafana-stack -n monitoring
kubectl describe svc grafana-stack -n monitoring
```

**Check port-forward:**
```bash
# Kill existing port-forwards
pkill -f "port-forward.*grafana"

# Restart
grafana-forward
```

### Prometheus Not Scraping Metrics

**Check Prometheus targets:**
```bash
# Port-forward to Prometheus
kubectl port-forward -n monitoring svc/grafana-stack-kube-prometh-prometheus 9090:9090

# Navigate to http://localhost:9090/targets
```

**Check ServiceMonitor resources:**
```bash
kubectl get servicemonitors -n monitoring
```

### Gatekeeper Not Enforcing Policies

**Check webhook configuration:**
```bash
kubectl get validatingwebhookconfigurations
kubectl describe validatingwebhookconfigurations gatekeeper-validating-webhook-configuration
```

**Check controller logs:**
```bash
kubectl logs -n gatekeeper-system -l control-plane=controller-manager
```

**Check constraint status:**
```bash
kubectl get constraints
kubectl describe <constraint-kind> <constraint-name>
```

**Verify audit results:**
```bash
kubectl logs -n gatekeeper-system -l control-plane=audit-controller
```

### HelmRelease Failures

**Check HelmRelease status:**
```bash
flux get helmreleases -A
kubectl describe helmrelease grafana-stack -n monitoring
kubectl describe helmrelease gatekeeper -n gatekeeper-system
```

**Check helm-controller logs:**
```bash
kubectl logs -n flux-system deploy/helm-controller
```

**Force reconciliation:**
```bash
flux reconcile helmrelease grafana-stack -n monitoring
flux reconcile helmrelease gatekeeper -n gatekeeper-system
```

### High Resource Usage

**Check resource consumption:**
```bash
kubectl top pods -n monitoring
kubectl top pods -n gatekeeper-system
```

**Reduce Prometheus retention:**
```yaml
# In grafana-stack-configmap.yaml
prometheus:
  prometheusSpec:
    retention: 3d  # Reduce from 7d
```

**Reduce storage:**
```yaml
prometheus:
  prometheusSpec:
    storageSpec:
      volumeClaimTemplate:
        spec:
          resources:
            requests:
              storage: 5Gi  # Reduce from 10Gi
```

## API Reference

### HelmRepository CRD

```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: HelmRepository
metadata:
  name: prometheus-community
  namespace: flux-system
spec:
  interval: 10m
  url: https://prometheus-community.github.io/helm-charts
```

### HelmRelease CRD

```yaml
apiVersion: helm.toolkit.fluxcd.io/v2
kind: HelmRelease
metadata:
  name: grafana-stack
  namespace: monitoring
spec:
  interval: 10m
  chart:
    spec:
      chart: kube-prometheus-stack
      version: '>=56.0.0'
      sourceRef:
        kind: HelmRepository
        name: prometheus-community
        namespace: flux-system
  install:
    crds: Create
    createNamespace: true
  upgrade:
    crds: CreateReplace
  valuesFrom:
    - kind: ConfigMap
      name: grafana-stack-values
      valuesKey: values.yaml
```

### Gatekeeper ConstraintTemplate

```yaml
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8srequiredlabels
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredLabels
      validation:
        openAPIV3Schema:
          properties:
            labels:
              type: array
              items:
                type: string
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8srequiredlabels
        violation[{"msg": msg, "details": {"missing_labels": missing}}] {
          provided := {label | input.review.object.metadata.labels[label]}
          required := {label | label := input.parameters.labels[_]}
          missing := required - provided
          count(missing) > 0
          msg := sprintf("you must provide labels: %v", [missing])
        }
```

### Gatekeeper Constraint

```yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequiredLabels
metadata:
  name: ns-must-have-admission
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Namespace"]
  parameters:
    labels: ["admission"]
```

## Maintenance

### Updating Grafana Stack

**Update version constraint:**
```yaml
# In grafana-stack-helmrelease.yaml
spec:
  chart:
    spec:
      version: '>=82.0.0'  # Update version
```

**Commit and push:**
```bash
git add workshop/foundation/flux-resources/grafana-stack-helmrelease.yaml
git commit -m "Update Grafana stack to v82.x"
git push
```

Flux will automatically upgrade on next reconciliation.

### Updating Gatekeeper

Similar process to Grafana Stack:

```yaml
# In gatekeeper-helmrelease.yaml
spec:
  chart:
    spec:
      version: '>=3.16.0'
```

### Backup and Restore

**Backup Grafana Dashboards:**
```bash
# Export all dashboards via API
kubectl port-forward -n monitoring svc/grafana-stack 3000:80 &
curl -u admin:admin123 http://localhost:3000/api/search | jq -r '.[].uid' | \
  xargs -I {} curl -u admin:admin123 http://localhost:3000/api/dashboards/uid/{} | \
  jq -r '.dashboard' > grafana-dashboards-backup.json
```

**Backup Gatekeeper Constraints:**
```bash
kubectl get constrainttemplates -o yaml > constraint-templates-backup.yaml
kubectl get constraints --all-namespaces -o yaml > constraints-backup.yaml
```

**Restore:**
```bash
kubectl apply -f constraint-templates-backup.yaml
kubectl apply -f constraints-backup.yaml
```

## Cleanup

### Remove via GitOps

```bash
# Remove the Kustomization
rm workshop/fluxcd/cluster/kind-5min-idp/workshop-foundation.yaml

# Commit and push
git add . && git commit -m "Remove foundation workshop"
git push

# Flux will automatically remove all resources
```

### Manual Cleanup

```bash
# Uninstall Helm releases
helm uninstall grafana-stack -n monitoring
helm uninstall gatekeeper -n gatekeeper-system

# Delete namespaces
kubectl delete namespace monitoring
kubectl delete namespace gatekeeper-system

# Remove CRDs (if desired)
kubectl delete crd constrainttemplates.templates.gatekeeper.sh
kubectl delete crd constraints.gatekeeper.sh
```

## Dependencies

- **Kubernetes:** v1.32.0+
- **FluxCD:** v2.7.5+
- **Helm:** v3.x (managed by Flux)
- **Storage:** Local-path-storage or equivalent StorageClass

## Security Considerations

1. **Grafana Credentials:**
   - Change default admin password in production
   - Use Kubernetes Secrets for sensitive values
   - Consider LDAP/OAuth integration

2. **Gatekeeper Policies:**
   - Test constraints in audit mode first
   - Use exemptions for system namespaces
   - Monitor constraint violations via audit logs

3. **Network Policies:**
   - Consider restricting ingress to Grafana
   - Limit Prometheus scrape targets
   - Secure AlertManager webhook endpoints

4. **RBAC:**
   - Limit access to monitoring namespace
   - Restrict Gatekeeper constraint management
   - Use separate service accounts for components

## Performance Considerations

- **Prometheus scrape interval:** 30s default (adjust for lower resource usage)
- **Metric retention:** 7 days (reduce for smaller storage requirements)
- **Grafana dashboard refresh:** Set appropriate intervals to reduce load
- **Gatekeeper audit interval:** Default 60s (increase for lower overhead)

## Additional Resources

- [kube-prometheus-stack Documentation](https://github.com/prometheus-operator/kube-prometheus)
- [Grafana Documentation](https://grafana.com/docs/)
- [Gatekeeper Documentation](https://open-policy-agent.github.io/gatekeeper/)
- [OPA Policy Language (Rego)](https://www.openpolicyagent.org/docs/latest/policy-language/)
- [FluxCD Helm Controller](https://fluxcd.io/flux/components/helm/)

---

**Document Version:** 1.0  
**Last Updated:** 2026-02-09  
**Workshop:** Foundation - Monitoring and Policy Management  
**Deployment:** GitOps via FluxCD
