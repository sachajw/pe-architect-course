# Debugging and Troubleshooting Guide

This document tracks common issues encountered during the platform setup and their solutions.

## Table of Contents

1. [Grafana Stack Issues](#grafana-stack-issues)
2. [Gatekeeper Issues](#gatekeeper-issues)
3. [FluxCD Issues](#fluxcd-issues)
4. [Kubernetes General Issues](#kubernetes-general-issues)

---

## Grafana Stack Issues

### Issue 1: Grafana Pod CrashLoopBackOff - Init Container Permission Denied

**Date:** 2026-02-09  
**Severity:** High  
**Component:** Grafana (kube-prometheus-stack)

#### Symptoms

```bash
$ kubectl get pods -n monitoring
NAME                             READY   STATUS                  RESTARTS   AGE
grafana-stack-77646c49db-dn7bs   0/3     Init:CrashLoopBackOff   6          7m
```

#### Root Cause

The `init-chown-data` init container fails with permission denied errors when trying to change ownership of directories in the persistent volume:

```bash
$ kubectl logs grafana-stack-77646c49db-dn7bs -n monitoring -c init-chown-data
chown: /var/lib/grafana/pdf: Permission denied
chown: /var/lib/grafana/png: Permission denied
chown: /var/lib/grafana/csv: Permission denied
```

**Why this happens:**
- Kind clusters use hostPath-based storage by default
- Init containers running as privileged may not have permissions to chown on hostPath volumes
- The init container attempts to run `chown -R 472:472 /var/lib/grafana`
- Fails on pre-existing directories with restrictive permissions

#### Investigation Commands

```bash
# Check pod status
kubectl get pods -n monitoring -l app.kubernetes.io/name=grafana

# Describe pod for detailed events
kubectl describe pod <pod-name> -n monitoring

# Check init container logs
kubectl logs <pod-name> -n monitoring -c init-chown-data

# Check PVC status
kubectl get pvc -n monitoring

# Check if volume is mounted
kubectl describe pod <pod-name> -n monitoring | grep -A 5 "Volumes:"
```

#### Solution

Disable the problematic init container and use Kubernetes-native `fsGroup` instead.

**Configuration change in `grafana-stack-configmap.yaml`:**

```yaml
grafana:
  # Fix for init container permission issues
  initChownData:
    enabled: false
  # Set security context with fsGroup instead
  securityContext:
    runAsUser: 472
    runAsGroup: 472
    fsGroup: 472
```

**Why this works:**
- `fsGroup` tells Kubernetes to automatically set ownership and permissions for mounted volumes
- No init container needed - Kubernetes handles it at mount time
- More reliable and Kubernetes-native approach

#### Apply the Fix

**Via GitOps (Recommended):**

```bash
# Update the ConfigMap in Git
vim workshop/foundation/flux-resources/grafana-stack-configmap.yaml

# Commit and push
git add workshop/foundation/flux-resources/grafana-stack-configmap.yaml
git commit -m "Fix Grafana init container permission issue"
git push

# Force reconciliation
flux reconcile source git flux-system
flux reconcile kustomization workshop-foundation
flux reconcile helmrelease grafana-stack -n monitoring
```

**Manual (Quick Fix):**

```bash
# Edit ConfigMap directly
kubectl edit configmap grafana-stack-values -n monitoring

# Add the configuration above, then restart the HelmRelease
flux reconcile helmrelease grafana-stack -n monitoring --timeout=5m
```

#### Verification

```bash
# Check new pod is running
kubectl get pods -n monitoring -l app.kubernetes.io/name=grafana

# Expected output:
# NAME                             READY   STATUS    RESTARTS   AGE
# grafana-stack-557b84749f-k26tj   3/3     Running   0          2m

# Verify no init containers
kubectl get pod -n monitoring -l app.kubernetes.io/name=grafana \
  -o jsonpath='{.items[0].spec.initContainers[*].name}'
# Should return empty (no init containers)

# Verify security context is set
kubectl get pod -n monitoring -l app.kubernetes.io/name=grafana \
  -o jsonpath='{.items[0].spec.securityContext.fsGroup}'
# Should return: 472
```

#### Prevention

- Always use `fsGroup` for volume permissions in Kubernetes
- Avoid init containers for simple permission fixes
- Test with kind clusters before deploying to production

#### Related Issues

- Similar issues may occur with other stateful applications (Prometheus, AlertManager)
- Solution pattern applies to any application requiring specific user/group ownership

---

## Gatekeeper Issues

### Issue Template (Add as issues occur)

**Date:**  
**Severity:**  
**Component:**  

#### Symptoms

```bash
# Command output showing the issue
```

#### Root Cause

Explanation of why the issue occurred.

#### Investigation Commands

```bash
# Commands used to diagnose
```

#### Solution

Steps to fix the issue.

#### Verification

```bash
# Commands to verify fix
```

---

## FluxCD Issues

### Issue Template (Add as issues occur)

**Date:**  
**Severity:**  
**Component:**  

#### Symptoms

```bash
# Command output showing the issue
```

#### Root Cause

Explanation of why the issue occurred.

#### Investigation Commands

```bash
# Commands used to diagnose
```

#### Solution

Steps to fix the issue.

#### Verification

```bash
# Commands to verify fix
```

---

## Kubernetes General Issues

### Issue Template (Add as issues occur)

**Date:**  
**Severity:**  
**Component:**  

#### Symptoms

```bash
# Command output showing the issue
```

#### Root Cause

Explanation of why the issue occurred.

#### Investigation Commands

```bash
# Commands used to diagnose
```

#### Solution

Steps to fix the issue.

#### Verification

```bash
# Commands to verify fix
```

---

## Quick Reference Commands

### Pod Debugging

```bash
# Get pod status
kubectl get pods -n <namespace>

# Describe pod (shows events and configuration)
kubectl describe pod <pod-name> -n <namespace>

# Get logs
kubectl logs <pod-name> -n <namespace>

# Get logs from specific container
kubectl logs <pod-name> -n <namespace> -c <container-name>

# Get logs from init container
kubectl logs <pod-name> -n <namespace> -c <init-container-name>

# Get previous container logs (after crash)
kubectl logs <pod-name> -n <namespace> --previous

# Follow logs
kubectl logs <pod-name> -n <namespace> -f

# Get pod YAML
kubectl get pod <pod-name> -n <namespace> -o yaml
```

### FluxCD Debugging

```bash
# Check all Flux components
flux check

# Get Kustomizations
flux get kustomizations

# Get HelmReleases
flux get helmreleases -A

# Get sources
flux get sources git
flux get sources helm

# Describe resource for details
kubectl describe kustomization <name> -n flux-system
kubectl describe helmrelease <name> -n <namespace>

# Check controller logs
kubectl logs -n flux-system deploy/source-controller
kubectl logs -n flux-system deploy/kustomize-controller
kubectl logs -n flux-system deploy/helm-controller

# Force reconciliation
flux reconcile source git flux-system
flux reconcile kustomization <name>
flux reconcile helmrelease <name> -n <namespace>

# Suspend/Resume
flux suspend kustomization <name>
flux resume kustomization <name>
```

### Helm Debugging

```bash
# List releases
helm list -A

# Get release status
helm status <release> -n <namespace>

# Get release values
helm get values <release> -n <namespace>

# Get release manifest
helm get manifest <release> -n <namespace>

# History
helm history <release> -n <namespace>

# Rollback
helm rollback <release> <revision> -n <namespace>
```

### Resource Inspection

```bash
# Get all resources in namespace
kubectl get all -n <namespace>

# Get specific resource types
kubectl get deployments,statefulsets,daemonsets -n <namespace>

# Get events
kubectl get events -n <namespace> --sort-by='.lastTimestamp'

# Get resource with labels
kubectl get pods -l app=<name> -n <namespace>

# Get resource usage
kubectl top pods -n <namespace>
kubectl top nodes

# Check PVC status
kubectl get pvc -n <namespace>
kubectl describe pvc <pvc-name> -n <namespace>
```

### Network Debugging

```bash
# Port forward to pod
kubectl port-forward pod/<pod-name> <local-port>:<remote-port> -n <namespace>

# Port forward to service
kubectl port-forward svc/<service-name> <local-port>:<remote-port> -n <namespace>

# Check service endpoints
kubectl get endpoints <service-name> -n <namespace>

# Test connectivity from a pod
kubectl run -it --rm debug --image=busybox --restart=Never -- sh
# Then inside: wget -O- http://<service>.<namespace>.svc.cluster.local
```

### Configuration Debugging

```bash
# Get ConfigMap
kubectl get configmap <name> -n <namespace> -o yaml

# Get Secret (base64 encoded)
kubectl get secret <name> -n <namespace> -o yaml

# Decode secret
kubectl get secret <name> -n <namespace> -o jsonpath='{.data.<key>}' | base64 -d
```

---

## Common Error Patterns

### CrashLoopBackOff

**Possible Causes:**
1. Application crashes immediately after start
2. Missing dependencies or configuration
3. Permission issues
4. Resource limits too low
5. Invalid command/arguments

**Debug Steps:**
```bash
kubectl logs <pod> -n <namespace>
kubectl describe pod <pod> -n <namespace>
kubectl get pod <pod> -n <namespace> -o yaml
```

### ImagePullBackOff

**Possible Causes:**
1. Image doesn't exist
2. Wrong image tag
3. Private registry without credentials
4. Network issues

**Debug Steps:**
```bash
kubectl describe pod <pod> -n <namespace> | grep -A 5 Events
kubectl get events -n <namespace> --field-selector involvedObject.name=<pod>
```

### Pending Pods

**Possible Causes:**
1. Insufficient resources (CPU/memory)
2. No nodes match affinity/taints
3. PVC not bound
4. Init containers failing

**Debug Steps:**
```bash
kubectl describe pod <pod> -n <namespace>
kubectl get nodes
kubectl top nodes
kubectl get pvc -n <namespace>
```

---

## Contributing

When adding new issues to this document:

1. Use the provided templates
2. Include actual command outputs (sanitized if needed)
3. Explain root cause clearly
4. Provide complete solution steps
5. Include verification commands
6. Add date and severity
7. Keep formatting consistent

---

**Document Version:** 1.0  
**Last Updated:** 2026-02-09  
**Maintained By:** Platform Engineering Team
