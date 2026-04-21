# Homelab Storage Implementation Plan

## Access Method: Tailscale DNS

Your machines are accessible via Tailscale DNS. Update `/etc/hosts` or use Tailscale hostnames directly.

### Common Tailscale Hostnames

```
# Check with: tailscale status
referb.tail-XXXXX.ts
blue1.tail-XXXXX.ts
blue2.tail-XXXXX.ts
```

### Quick Connect

```bash
# Test Tailscale connectivity
tailscale status

# SSH via Tailscale (replace XXXXX)
ssh referb.tail-XXXXX.ts
```

---

## Current Infrastructure

### Kubernetes Cluster
| Node | Role | IP (LAN) | Tailscale IP |
|------|------|----------|--------------|
| blue1 | control-plane, etcd | 192.168.1.128 | 100.x.x.x |
| blue2 | worker | 192.168.1.11 | 100.x.x.x |
| refurb | worker | 192.168.1.253 | 100.x.x.x |

### Storage Classes Available
- `longhorn` (default) - Block storage
- `local-path` - Local path storage
- `longhorn-static` - Static Longhorn volumes

### Current Deployments - Issues
- **Longhorn**: Running (v1.7.2), CSI plugin has issues on refurb node
- **SeaweedFS**: Partially running
  - Volume (8080/tcp): Running ✓
  - S3 (8333): Running ✓
  - Master (9333): CrashLoopBackOff ✗
  - Filer (8888): CrashLoopBackOff ✗

### Model Serving
- **Host**: pedrogpt (Tailscale hostname)
- **Endpoint**: http://pedrogpt:8080/v1
- **Model**: qwen3-coder-30b (loaded)
- **Type**: llama.cpp (standalone, not in K8s)

---

## Implementation Plan

### Phase 1: Fix SeaweedFS (Priority: High)

The master and filer are crashing. Options:

```bash
# Option A: Fix existing deployment
kubectl rollout restart deployment seaweedfs -n seaweedfs

# Option B: Redeploy (clean)
kubectl delete ns seaweedfs
helm install seaweedfs seaweedfs/seaweedfs -n seaweedfs --create-namespace

# Option C: Skip SeaweedFS, use Longhorn NFS instead
# Use Longhorn with RWX access mode for shared corpus
```

### Phase 2: Create Storage for Experiments

```yaml
# experiments-storage.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: experiments-corpus
  namespace: experiments
spec:
  accessModes:
    - ReadWriteMany
  storageClassName: longhorn
  resources:
    requests:
      storage: 100Gi
```

Apply with:
```bash
kubectl create ns experiments
kubectl apply -f config/storage.yaml
```

### Phase 3: Deploy Model Serving (Priority: High)

No model serving currently deployed. Choose one:

#### Option A: vLLM (Recommended)
```bash
# Deploy vLLM with GPU
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vllm
  namespace: experiments
spec:
  replicas: 1
  selector:
    matchLabels:
      app: vllm
  template:
    metadata:
      labels:
        app: vllm
    spec:
      containers:
      - name: vllm
        image: vllm/vllm-openai:latest
        ports:
        - containerPort: 8000
        env:
        - name: VLLM_HOST_IP
          value: "0.0.0.0"
        - name: VLLM_MODEL
          value: "qwen2.5-coder-32b-instruct"
        resources:
          limits:
            nvidia.com/gpu: 1
---
apiVersion: v1
kind: Service
metadata:
  name: vllm
  namespace: experiments
spec:
  selector:
    app: vllm
  ports:
  - port: 8000
    targetPort: 8000
EOF
```

#### Option B: Ollama on Tailscale Node (Simpler)

Run directly on a host with GPU:
```bash
# On referb (or any Tailscale node with GPU)
sudo systemctl enable --now ollama
ollama serve
# Available at http://referb:11434
```

### Phase 4: Client Access (from macOS)

```bash
# Via Tailscale - no extra config needed!
# Just use the Tailscale IP/hostname

# Example endpoints after setup:
# Model: http://referb.tail-XXXXX.ts:8000/v1
# S3: http://referb.tail-XXXXX.ts:8333
# Corpus: sshfs referb.tail-XXXXX.ts:/path /mnt/homelab
```

---

## Storage Architecture Summary

```
┌─────────────────────────────────────────────────────────────────────┐
│                   Homelab (via Tailscale)                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Longhorn (K8s Block)                      │   │
│  │  • experiments-corpus (100Gi, RWX) - corpus files           │   │
│  │  • experiments-db (20Gi, RWO) - SQLite/Chroma               │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                   SeaweedFS (Object)                         │   │
│  │  • S3 API: http://referb:8333  (Tailscale)                 │   │
│  │  • Volume: http://referb:8080                              │   │
│  │  • Status: S3✓ Volume✓ Master✗ Filer✗                     │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Model Serving                              │   │
│  │  • Option A: K8s vLLM (in experiments namespace)            │   │
│  │  • Option B: Ollama on host (via Tailscale)                 │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                               │
                    Tailscale VPN
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     macOS Developer Machine                          │
│                                                                      │
│  experiments/ repo                                                  │
│  • Access via Tailscale hostnames                                   │
│  • Model: http://<host>.tail-XXXXX.ts:8000                         │
│  • Storage: sshfs or direct access                                  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Updated Connection Test

```bash
# Test with Tailscale hostnames (update XXXXX)
curl -s http://referb.tail-XXXXX.ts:8333  # SeaweedFS S3
curl -s http://referb.tail-XXXXX.ts:8080  # SeaweedFS Volume
curl -s http://referb.tail-XXXXX.ts:8000/v1/models  # Model (when deployed)
```

---

## Action Items

1. **Check Tailscale status** - Get hostnames: `tailscale status`
2. **Update config** - Set correct Tailscale hostnames in `config/model-gateway.yaml`
3. **Fix SeaweedFS** - Redeploy or use Longhorn only
4. **Deploy models** - Choose vLLM (K8s) or Ollama (host)
5. **Create PVCs** - `kubectl apply -f config/storage.yaml`