#!/usr/bin/env bash
set -euo pipefail
[[ ${EUID:-$(id -u)} -eq 0 ]] || { echo "Run with sudo."; exit 1; }
rm -f /usr/local/bin/lkoc
rm -rf /opt/lkoc
echo "LKOC program files removed. kubeconfig and Kubernetes resources were not modified."
