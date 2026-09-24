# Administrator Manual

## Linux Kubernetes Operations Center - Advanced

Version 1.0.0  
Designed and Development by : antonios.mortos@outlook.com

## Architecture

LKOC is a local control-plane client using your existing kubeconfig:

```text
ANSI TUI / CLI
      │
      ├── kubectl
      │    ├── cluster contexts
      │    ├── nodes / namespaces / pods
      │    ├── workloads
      │    ├── networking
      │    ├── storage
      │    ├── events / logs
      │    └── scale / restart / apply
      │
      ├── helm (optional)
      └── velero (optional)
```

LKOC does not install an in-cluster agent and does not bypass Kubernetes RBAC.

## Installation

```bash
sudo ./install.sh
lkoc --version
lkoc doctor
```

Before first use:

```bash
kubectl config get-contexts
kubectl cluster-info
kubectl get nodes
```

## Cluster contexts

Use **Clusters / Contexts** to select a context inside LKOC. The selection is passed as `kubectl --context ...`; LKOC does not rewrite kubeconfig `current-context`, preventing unexpected changes in another shell.

## Main operational views

The dashboard provides cluster health based on node readiness, pod state and recent Kubernetes data. Dedicated screens expose Nodes, Namespaces, Pods, Deployments, StatefulSets, DaemonSets, Services, Ingresses, PVCs, StorageClasses, Jobs, CronJobs, RBAC objects and NetworkPolicies.

## Logs

TUI: select **Logs**, select a pod, and LKOC reads recent log lines.

CLI:

```bash
lkoc --context CLUSTER logs NAMESPACE POD --tail 500
```

## Scale deployment

```bash
lkoc --context CLUSTER scale NAMESPACE DEPLOYMENT REPLICAS
```

The TUI validates that the replica count is numeric.

## Rollout restart

The TUI requires the operator to type `YES` before issuing a restart.

```bash
lkoc --context CLUSTER restart NAMESPACE DEPLOYMENT
```

## Apply manifest

The TUI checks that the file exists and requires `APPLY` before running the operation.

```bash
lkoc --context CLUSTER apply manifest.yaml
```

## Helm

If `helm` is in PATH, LKOC displays releases across namespaces. It does not automatically install Helm.

## Velero

If the Velero CLI is installed and the cluster is already configured for Velero, LKOC can list backups, create backups and create restores. It does not install Velero into the cluster automatically.

Verify first:

```bash
velero version
velero backup-location get
```

## Alerts

The initial alert screen combines non-Running/non-Succeeded pod states and recent Kubernetes `Warning` events. A future backend can integrate Prometheus/Alertmanager without changing the ANSI UI contract.

## Security

LKOC uses the credentials already referenced by kubeconfig and never copies them into project configuration. Use least-privilege RBAC, separate admin contexts and short-lived credentials where available.

Inspect permissions with:

```bash
kubectl auth can-i --list
```

## Troubleshooting

Start with:

```bash
lkoc doctor
kubectl config current-context
kubectl get nodes
```

A `Forbidden` error generally indicates RBAC authorization, not an LKOC rendering problem.

## ANSI rendering

Every screen is rendered by one common engine. It detects terminal width, excludes ANSI escape codes from visible-length calculations, clips long values, pads rows, then draws the right border at one fixed column.

Recommended terminal size is at least 120x35.

---

Designed and Development by : antonios.mortos@outlook.com
