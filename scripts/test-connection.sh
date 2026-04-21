#!/bin/bash
# Test connectivity to homelab services
# Usage: ./scripts/test-connection.sh

set -e

echo "=== Testing Experiment Infrastructure ==="

# Test 1: Tailscale
echo -n "1. Tailscale... "
if command -v tailscale &> /dev/null && tailscale status &>/dev/null; then
  echo "OK (Tailscale running)"
elif kubectl get pods -n tailscale &>/dev/null; then
  echo "OK (Tailscale operator)"
else
  echo "NOT FOUND"
fi

# Test 2: K8s API
echo -n "2. Kubernetes API... "
if kubectl cluster-info &>/dev/null; then
  echo "OK"
else
  echo "FAIL"
fi

# Test 3: vLLM (pedrogtp)
echo -n "3. vLLM (100.87.122.109:8080)... "
if curl -sf --connect-timeout 5 http://100.87.122.109:8080/v1/models &>/dev/null; then
  echo "OK"
else
  echo "NOT REACHABLE (from this machine)"
fi

# Test 4: SeaweedFS S3 (if accessible)
echo -n "4. SeaweedFS S3... "
if curl -sf --connect-timeout 5 http://referb:8333 &>/dev/null 2>&1; then
  echo "OK"
else
  echo "NOT REACHABLE"
fi

# Test 5: Longhorn storage
echo -n "5. Longhorn storage class... "
if kubectl get storageclass longhorn &>/dev/null; then
  echo "OK"
else
  echo "FAIL"
fi

# Test 6: Local mount (if mounted)
echo -n "6. Local mount (/mnt/homelab)... "
if mount | grep -q "/mnt/homelab"; then
  echo "OK"
else
  echo "NOT MOUNTED (run connect-storage.sh)"
fi

echo ""
echo "=== Next Steps ==="
echo "1. Ensure Tailscale is running on this machine"
echo "2. Test vLLM: curl http://100.87.122.109:8080/v1/models"
echo "3. If vLLM works, update config/model-gateway.yaml with correct URL"
echo "4. Create namespace: kubectl create ns experiments"