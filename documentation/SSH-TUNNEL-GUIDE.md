# SSH Tunnel Setup Guide — Coder Workspace (5min-IDP)

This guide documents all configuration changes made to expose the Kind cluster services in the `pangarabbit.coder` Coder workspace to a local browser via SSH port forwarding.

---

## Architecture Overview

```
Local Browser
     │
     │ http://<service>.127.0.0.1.sslip.io:8888
     │
127.0.0.1:8888 ──── SSH Tunnel ──── pangarabbit.coder
                                          │
                                     port 80 (Kind ingress)
                                          │
                               nginx Ingress Controller
                              ┌────────────┼────────────┐
                          teams-ui    keycloak     grafana
                         (Angular)  (Auth/OIDC)  (Metrics)
                                          │
                                     teams-api
                                     (FastAPI)
```

**sslip.io wildcard DNS** resolves any hostname containing an IP address back to that IP. For example, `teams-ui.127.0.0.1.sslip.io` resolves to `127.0.0.1`, which is the local end of the SSH tunnel.

---

## SSH Configuration

**File:** `~/.ssh/config`

```ssh-config
Host pangarabbit.coder
    HostName pangarabbit.coder
    User root
    # Port forwards: local_port → remote_host:remote_port (inside Coder workspace)
    LocalForward 8888 localhost:80      # Kind ingress HTTP  → all services
    LocalForward 8443 localhost:443     # Kind ingress HTTPS
    LocalForward 16443 localhost:6443   # Kubernetes API     → next tool
```

> **Note:** Port 8888 is used instead of the common 8080 to avoid conflicts with local development servers.

### Starting the Tunnel

```bash
ssh -f pangarabbit.coder -N
```

The `-f` flag runs SSH in the background. `-N` means no remote command (forwarding only).

### Verifying the Tunnel

```bash
# Check SSH process is running
ps aux | grep "ssh.*pangarabbit"

# Test a service
curl -sI http://teams-ui.127.0.0.1.sslip.io:8888
```

---

## Service URLs

| Service       | URL                                                 | Notes                     |
|---------------|-----------------------------------------------------|---------------------------|
| Teams UI      | http://teams-ui.127.0.0.1.sslip.io:8888            | Angular frontend          |
| Teams API     | http://teams-api.127.0.0.1.sslip.io:8888           | FastAPI backend           |
| Keycloak      | http://platform-auth.127.0.0.1.sslip.io:8888       | OIDC auth server          |
| Grafana       | http://grafana.127.0.0.1.sslip.io:8888             | Monitoring dashboards     |

---

## Kind Cluster Topology

The Coder workspace runs a Kind (Kubernetes in Docker) cluster named `5min-idp`. The Kind control-plane container maps these ports to the workspace host:

| Container Port | Host Port | Purpose              |
|----------------|-----------|----------------------|
| 80             | 80        | nginx ingress HTTP   |
| 443            | 443       | nginx ingress HTTPS  |
| 6443           | 6443      | Kubernetes API       |

The SSH `LocalForward` entries connect local ports to these host ports inside the workspace.

---

## next Tool (Capacitor Next)

The `next` Kubernetes UI tool is configured to connect to the remote Kind cluster via the `16443` port forward.

**Kubeconfig:** `~/.kube/cfg/coder/config-coder.yaml`

The kubeconfig was copied from `/root/.kube/config` inside the workspace and the `server` URL was changed from `https://127.0.0.1:6443` to `https://localhost:16443`.

**Running next:**

```bash
# Start the SSH tunnel first
ssh -f pangarabbit.coder -N

# Then launch next
next -p 4739 --kubeconfig ~/.kube/cfg/coder/config-coder.yaml
```

Open http://localhost:4739 in your browser.

> The `switch` tool (`~/.kube/cfg/`) can be used to switch between kubeconfig files, including `config-coder.yaml`.

---

## GitOps Changes

All changes are tracked in Flux CD kustomizations. The relevant kustomizations are:

| Kustomization         | Path                                                     |
|-----------------------|----------------------------------------------------------|
| `workshop-teams-app`  | `./workshop/teams-management/teams-app/flux-resources`  |
| `workshop-keycloak`   | `./workshop/teams-management/keycloak/flux-resources`   |

### Problem: Angular App Has Hardcoded URLs Without Port

The compiled Angular bundle (`main.*.js`) contains hardcoded URLs:
- `http://teams-api.127.0.0.1.sslip.io` (no port)
- `http://platform-auth.127.0.0.1.sslip.io` (no port)

These fail through the SSH tunnel because the tunnel uses port **8888**, not port **80**.

### Fix: nginx sub_filter URL Rewriting

Rather than rebuilding the Docker image, the teams-ui nginx server rewrites URLs in the served JavaScript bundle at runtime using nginx `sub_filter`.

**File:** `workshop/teams-management/teams-app/flux-resources/configmap.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: teams-ui-nginx-config
  namespace: engineering-platform
data:
  default.conf: |
    server {
        listen 80;
        server_name localhost;
        root /usr/share/nginx/html;
        index index.html;

        # Rewrite hardcoded URLs to include port 8888 (SSH tunnel port)
        sub_filter "http://teams-api.127.0.0.1.sslip.io" "http://teams-api.127.0.0.1.sslip.io:8888";
        sub_filter "http://platform-auth.127.0.0.1.sslip.io" "http://platform-auth.127.0.0.1.sslip.io:8888";
        sub_filter_once off;
        sub_filter_types application/javascript;

        location / {
            try_files $uri $uri/ /index.html;
        }

        location /api/ {
            proxy_pass http://teams-api-service:8000/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
```

The ConfigMap is mounted into the teams-ui pod to replace `/etc/nginx/conf.d/default.conf`.

**Deployment changes** (`deployment.yaml`):
```yaml
volumeMounts:
- name: nginx-config
  mountPath: /etc/nginx/conf.d/default.conf
  subPath: default.conf
volumes:
- name: nginx-config
  configMap:
    name: teams-ui-nginx-config
```

---

## Keycloak Configuration

### Problem: KC_HOSTNAME Without Port

Keycloak's `KC_HOSTNAME` was set to `platform-auth.127.0.0.1.sslip.io` (no port). The well-known OIDC discovery endpoint returned URLs without `:8888`, causing `keycloak-js` to call the wrong endpoints.

**Fix:** Use `KC_HOSTNAME_URL` (Keycloak 22+ Quarkus) to set the full base URL including port.

```yaml
env:
- name: KC_HOSTNAME_URL
  value: "http://platform-auth.127.0.0.1.sslip.io:8888"
- name: KC_HOSTNAME_STRICT
  value: "false"
- name: KC_HTTP_ENABLED
  value: "true"
- name: KC_HOSTNAME_STRICT_HTTPS
  value: "false"
- name: KC_PROXY
  value: "edge"
```

### Problem: nginx Ingress CORS Conflict

The Keycloak ingress originally had nginx CORS annotations:
```yaml
nginx.ingress.kubernetes.io/enable-cors: "true"
nginx.ingress.kubernetes.io/cors-allow-origin: "*"
```

**Why this breaks auth:** The combination of `Access-Control-Allow-Origin: *` and `Access-Control-Allow-Credentials: true` is invalid per the CORS spec. Keycloak sets `credentials: true` because the token endpoint requires it. Browsers reject the response when both headers appear.

**Fix:** Remove ALL nginx CORS annotations from the Keycloak ingress. Keycloak handles its own CORS via the `webOrigins` setting on each client. No env vars like `KC_HTTP_CORS_*` are needed.

### Keycloak `teams-ui` Client Configuration

The `teams-ui` client in the `teams` realm must have:

**`redirectUris`** — URLs that Keycloak may redirect back to after login:
```json
[
  "http://teams-ui.127.0.0.1.sslip.io/*",
  "http://teams-ui.127.0.0.1.sslip.io:8888/*",
  "http://localhost:4200/*"
]
```

> Do NOT include `http://platform-auth.127.0.0.1.sslip.io/*` here — that was a misconfiguration that allowed Keycloak to redirect back to its own token endpoint (causing 405 errors).

**`webOrigins`** — Origins allowed to make cross-origin requests to Keycloak (controls CORS):
```json
[
  "http://teams-ui.127.0.0.1.sslip.io",
  "http://teams-ui.127.0.0.1.sslip.io:8888",
  "http://localhost:4200"
]
```

**Verify CORS is working correctly:**
```bash
curl -sI -X OPTIONS \
  -H "Origin: http://teams-ui.127.0.0.1.sslip.io:8888" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type" \
  "http://platform-auth.127.0.0.1.sslip.io:8888/realms/teams/protocol/openid-connect/token"
```

Expected response should include:
```
Access-Control-Allow-Origin: http://teams-ui.127.0.0.1.sslip.io:8888
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: POST, OPTIONS
```

> If you see `Access-Control-Allow-Origin: *` alongside `Access-Control-Allow-Credentials: true`, there are still nginx CORS annotations present on the ingress — remove them.

### Realm Import and Live Updates

Keycloak uses `--import-realm` with `IGNORE_EXISTING` behaviour. This means:
- On first start: the realm is created from the ConfigMap JSON
- On subsequent starts: the import is **skipped** (realm already exists in postgres)

To apply changes to an existing realm (e.g., adding redirect URIs), use `kcadm.sh` directly:

```bash
# Exec into the Keycloak pod
kubectl exec -n keycloak deploy/keycloak -- bash

# Authenticate
/opt/keycloak/bin/kcadm.sh config credentials \
  --server http://localhost:8080 \
  --realm master \
  --user admin \
  --password admin

# Get the teams-ui client UUID
/opt/keycloak/bin/kcadm.sh get clients -r teams --fields id,clientId

# Update redirect URIs (replace <UUID> with the actual ID)
/opt/keycloak/bin/kcadm.sh update clients/<UUID> -r teams \
  -s 'redirectUris=["http://teams-ui.127.0.0.1.sslip.io:8888/*","http://teams-ui.127.0.0.1.sslip.io/*","http://localhost:4200/*"]'
```

---

## Grafana Ingress

Grafana was exposed only via NodePort (30300). An ingress was added to make it accessible via the tunnel:

```bash
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: grafana-ingress
  namespace: monitoring
spec:
  ingressClassName: nginx
  rules:
  - host: grafana.127.0.0.1.sslip.io
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: grafana
            port:
              number: 80
EOF
```

This is tracked in `workshop/monitoring/grafana-ingress.yaml` (or applied inline).

---

## Test Credentials

| Username    | Password     | Role         |
|-------------|--------------|--------------|
| `teamlead1` | `password123`| team-leader  |
| `admin`     | `admin123`   | admin        |

---

## Troubleshooting

### White page on teams-ui

1. Check the tunnel is running: `ps aux | grep "ssh.*pangarabbit"`
2. Check the nginx ConfigMap is mounted: `kubectl describe pod -n engineering-platform -l app=teams-ui | grep -A5 Volumes`
3. Verify sub_filter is active: `curl -s http://teams-ui.127.0.0.1.sslip.io:8888/main.*.js | grep 'platform-auth.*:8888'`

### Keycloak login redirects to wrong URL (405 on token endpoint)

This happens when `platform-auth.*` is in the `redirectUris` list. Remove it with `kcadm.sh` as shown above. The token endpoint only accepts POST; a GET means Keycloak redirected the browser there instead of back to the app.

### CORS error on Keycloak token endpoint

Check that no nginx CORS annotations are on the Keycloak ingress:
```bash
kubectl get ingress -n keycloak keycloak-ingress -o jsonpath='{.metadata.annotations}'
```
Output should be empty `{}` or only contain non-CORS annotations.

### SSH tunnel drops

If the tunnel disconnects, restart it:
```bash
# Kill existing
pkill -f "ssh.*pangarabbit.coder"
# Reconnect
ssh -f pangarabbit.coder -N
```

### Flux not applying changes

```bash
# Force reconcile
flux reconcile kustomization workshop-keycloak --with-source
flux reconcile kustomization workshop-teams-app --with-source

# Check status
flux get kustomizations
```

---

## Files Changed Summary

| File | Change |
|------|--------|
| `~/.ssh/config` | Added `HostName`, `LocalForward 8888/8443/16443` for `pangarabbit.coder` |
| `~/.kube/cfg/coder/config-coder.yaml` | Kubeconfig pointing to `localhost:16443` |
| `~/.kube/cfg/coder/README.md` | Documentation for coder kubeconfig |
| `workshop/teams-management/teams-app/flux-resources/configmap.yaml` | nginx ConfigMap with sub_filter URL rewrite |
| `workshop/teams-management/teams-app/flux-resources/deployment.yaml` | Volume mount for nginx ConfigMap |
| `workshop/teams-management/teams-app/flux-resources/kustomization.yaml` | Added `configmap.yaml` to resources |
| `workshop/teams-management/keycloak/keycloak.yaml` | `KC_HOSTNAME_URL` with `:8888`, removed CORS annotations, fixed redirectUris/webOrigins |
