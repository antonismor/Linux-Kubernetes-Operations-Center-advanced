# Linux Kubernetes Operations Center - Advanced

**Linux Kubernetes Operations Center - Advanced (LKOC)** is an open-source, terminal-native Kubernetes operations console for Linux administrators who want a fast operational view of one or more Kubernetes clusters without installing a separate in-cluster management agent.

It provides a custom ANSI/Unicode TUI, standard CLI commands for automation, multi-context navigation, workload and storage visibility, events, logs, safe operational actions, Helm inventory, and optional Velero backup/restore integration.

**Current release:** `1.0.0`  
**License:** MIT  
**Designed and Development by : antonios.mortos@outlook.com**

---

## Overview

LKOC uses the same kubeconfig and Kubernetes identity that `kubectl` already uses.

```text
                         ┌─────────────────────────────┐
                         │   ANSI TUI / CLI - LKOC    │
                         └──────────────┬──────────────┘
                                        │
                               existing kubeconfig
                                        │
                                  ┌─────▼─────┐
                                  │  kubectl  │
                                  └─────┬─────┘
                                        │
          ┌─────────────────────────────┼─────────────────────────────┐
          │                             │                             │
     Cluster inventory             Operations                 Optional tools
          │                             │                             │
   Nodes / Pods / NS          Logs / Scale / Restart            Helm / Velero
   Workloads / Storage         Apply / Events / RBAC
   Services / Ingress          NetworkPolicies / Jobs
```

LKOC does **not** bypass Kubernetes RBAC, does **not** copy cluster credentials into its own configuration, and does **not** require an LKOC agent or daemon inside your cluster.

---

## Main capabilities

### Multi-cluster / context management

- Reads contexts directly from kubeconfig
- Shows the currently selected context
- Lets the operator switch cluster context inside LKOC
- Passes the selected context explicitly to `kubectl --context`
- Does not rewrite kubeconfig `current-context` during an LKOC session

### Cluster operations views

- Nodes and Ready/NotReady state
- Namespaces
- Pods across all namespaces
- Deployments
- StatefulSets
- DaemonSets
- Services
- Ingress resources
- PersistentVolumeClaims
- StorageClasses
- Jobs
- CronJobs
- recent Kubernetes Events
- RBAC summary
- NetworkPolicy inventory
- operational warning view

### Operational actions

- Pod log viewing
- Deployment scaling
- Deployment rollout restart
- Kubernetes manifest apply
- Velero backup creation
- Velero restore creation

### Optional integrations

- **Helm** — list releases across namespaces
- **Velero** — list/create backups and create restores

---

## ANSI terminal interface

LKOC is intentionally terminal-native. It does not use image assets, browser pages, or a desktop GUI.

```text
╔══════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ ◆ LINUX KUBERNETES OPERATIONS CENTER - ADVANCED                              v1.0.0  22:00:00     ║
║   Current cluster context: prod-cluster                                                              ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════╣
║┌─ DASHBOARD ────────────────────────────────────────────────────────────────────────────────────────┐║
║│ CONTEXT                    NODES     PODS      NAMESPACES    DEPLOYMENTS    HEALTH                 │║
║│ ────────────────────────────────────────────────────────────────────────────────────────────────── │║
║│ prod-cluster               5         42        8             14             ● HEALTHY              │║
║└────────────────────────────────────────────────────────────────────────────────────────────────────┘║
║                                                                                                      ║
║┌─ MAIN MENU ────────────────────────────────────────────────────────────────────────────────────────┐║
║│  ▶  Dashboard                                                                                     │║
║│     Clusters / Contexts                                                                           │║
║│     Nodes                                                                                         │║
║│     Namespaces                                                                                    │║
║│     Pods                                                                                          │║
║│     Deployments                                                                                   │║
║│     StatefulSets                                                                                  │║
║│     DaemonSets                                                                                    │║
║│     Services                                                                                      │║
║│     Ingress                                                                                       │║
║│     Storage (PVC / StorageClasses)                                                                │║
║│     Helm Releases                                                                                 │║
║│     Recent Events                                                                                 │║
║│     Logs                                                                                          │║
║│     Scale Deployment                                                                              │║
║│     Rollout Restart                                                                               │║
║│     Apply Manifest                                                                                │║
║│     Backup & Restore (Velero)                                                                     │║
║│     Security & RBAC                                                                               │║
║│     Network Policies                                                                              │║
║│     Jobs & CronJobs                                                                               │║
║│     Alerts                                                                                        │║
║│     Doctor / Diagnostics                                                                          │║
║│     Exit                                                                                          │║
║└────────────────────────────────────────────────────────────────────────────────────────────────────┘║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ ↑/↓ Navigate  ENTER Select  ESC Back  F1 Help  F5 Refresh                             ● READY       ║
║ Designed and Development by : antonios.mortos@outlook.com                                           ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════╝
```

The renderer measures **visible** text width after removing ANSI escape sequences, clips oversized values, pads every row to a deterministic width, and only then draws the right-hand border. This keeps the side borders aligned even when status fields use terminal colors or Kubernetes resource names are long.

Recommended terminal:

```text
UTF-8 terminal
120 columns or wider
35 rows or taller
TERM=xterm-256color recommended
```

---

# Installation

## Requirements

Required:

- Linux
- Python 3.10 or newer
- `kubectl`
- working kubeconfig
- network access to the Kubernetes API server

Optional:

- `helm` for Helm release inventory
- `velero` for backup and restore features
- `jq` for administrator-side JSON inspection

Your Kubernetes cluster can be local, remote, bare-metal, VM-based, managed Kubernetes, or any environment that standard `kubectl` can access.

## Clone the repository

```bash
git clone https://github.com/antonismor/Linux-Kubernetes-Operations-Center-advanced.git
cd Linux-Kubernetes-Operations-Center-advanced
```

## Install LKOC

```bash
sudo ./install.sh
```

The installer places:

```text
/opt/lkoc/             application package
/usr/local/bin/lkoc    command wrapper
```

The installer does **not** modify your kubeconfig or Kubernetes resources.

## Verify

```bash
lkoc --version
lkoc doctor
```

Expected version:

```text
lkoc 1.0.0
```

---

# Before the first run

Confirm that your Kubernetes client works independently of LKOC:

```bash
kubectl config get-contexts
kubectl config current-context
kubectl cluster-info
kubectl get nodes
```

If these commands do not work, fix kubeconfig, networking, certificates, or RBAC first.

Then launch:

```bash
lkoc
```

Normal LKOC operation does **not** require root. Permissions come from your Kubernetes credentials and RBAC.

---

# Keyboard navigation

```text
↑ / ↓       Move through menus
ENTER       Select
ESC         Back / leave menu
q / Q       Back / leave menu where supported
Ctrl+C      Emergency exit
```

---

# Cluster contexts

List contexts from the CLI:

```bash
lkoc contexts
```

Inside the TUI choose:

```text
Clusters / Contexts
```

Selecting a context inside LKOC does not permanently overwrite kubeconfig `current-context`. LKOC passes the context to individual commands explicitly.

This is useful when an administrator has, for example:

```text
prod-cluster
dev-cluster
test-cluster
customer-a
customer-b
```

in the same kubeconfig.

---

# Read-only inventory

The following views are intended primarily for inspection:

```text
Nodes
Namespaces
Pods
Deployments
StatefulSets
DaemonSets
Services
Ingress
Storage (PVC / StorageClasses)
Helm Releases
Recent Events
Security & RBAC
Network Policies
Jobs & CronJobs
Alerts
```

CLI examples follow.

## Nodes

```bash
lkoc --context prod-cluster get nodes
```

## Pods

```bash
lkoc --context prod-cluster get pods
```

## Namespaces

```bash
lkoc --context prod-cluster get namespaces
```

## Deployments

```bash
lkoc --context prod-cluster get deployments
```

## StatefulSets

```bash
lkoc --context prod-cluster get statefulsets
```

## DaemonSets

```bash
lkoc --context prod-cluster get daemonsets
```

## Services

```bash
lkoc --context prod-cluster get services
```

## Ingresses

```bash
lkoc --context prod-cluster get ingresses
```

## PVCs

```bash
lkoc --context prod-cluster get pvcs
```

## Events

```bash
lkoc --context prod-cluster get events
```

CLI query output is JSON so that it can also be piped into other tools.

---

# Pod logs

From the TUI:

```text
Logs
  → select Pod
  → display recent log lines
```

From CLI:

```bash
lkoc --context prod-cluster logs production web-7fd89c --tail 300
```

LKOC delegates access to `kubectl logs`; normal Kubernetes permissions still apply.

---

# Scaling deployments

TUI:

```text
Scale Deployment
  → select deployment
  → enter replica count
```

CLI:

```bash
lkoc --context prod-cluster scale production api 5
```

Equivalent Kubernetes operation:

```bash
kubectl --context prod-cluster -n production scale deployment api --replicas 5
```

---

# Rollout restart

TUI restart requires the operator to type:

```text
YES
```

before LKOC submits the action.

CLI:

```bash
lkoc --context prod-cluster restart production api
```

This maps to a Kubernetes deployment rollout restart.

---

# Apply a manifest

TUI:

```text
Apply Manifest
  → enter manifest path
  → type APPLY
```

CLI:

```bash
lkoc --context prod-cluster apply deployment.yaml
```

Review manifests before applying them to production clusters.

---

# Helm integration

If Helm is installed:

```bash
helm version
helm list -A
```

LKOC exposes **Helm Releases** and shows release name, namespace, revision, status, chart and application version where available.

LKOC 1.0.0 does not automatically install Helm.

---

# Velero backup & restore

Velero support is optional.

Before using it in LKOC, Velero should already work:

```bash
velero version
velero backup-location get
```

The TUI supports:

```text
Backup & Restore (Velero)
├── List Backups
├── Create Backup
└── Create Restore
```

Backup creation requires explicit confirmation:

```text
BACKUP
```

Restore creation requires:

```text
RESTORE
```

LKOC does not install or configure Velero automatically. Backup locations, credentials, snapshot plugins, object storage and retention remain part of the administrator's Velero deployment.

---

# Security and RBAC

LKOC does not elevate Kubernetes permissions.

The selected kubeconfig identity remains authoritative.

Inspect permissions with:

```bash
kubectl auth can-i --list
kubectl auth can-i list pods -A
kubectl auth can-i patch deployments -n production
```

The **Security & RBAC** view summarizes:

- ClusterRoles
- ClusterRoleBindings
- namespaced Roles
- namespaced RoleBindings

LKOC deliberately does not print Secret resource payloads.

Recommended production practices:

- use least-privilege RBAC
- protect kubeconfig files and private keys
- prefer short-lived authentication where available
- keep production contexts clearly named
- audit cluster-admin use
- review manifests before apply operations
- treat scale/restart/restore operations as production changes

---

# NetworkPolicy inventory

Choose:

```text
Network Policies
```

to inspect existing NetworkPolicy resources across namespaces.

The view includes:

- namespace
- policy name
- pod selector
- policy types

Version 1.0.0 is inspection-focused; it does not provide a NetworkPolicy rule editor.

---

# Alerts

The initial built-in warning view combines:

- pods whose state is not `Running` or `Succeeded`
- recent Kubernetes `Warning` Events
- dashboard visibility of NotReady nodes

This is an operational overview, not a replacement for Prometheus/Alertmanager.

A future backend can integrate metrics and alerting systems while preserving the same ANSI interface.

---

# Doctor / diagnostics

Run:

```bash
lkoc doctor
```

It reports:

- Linux platform
- Python version
- kubeconfig path
- `kubectl` availability
- Helm availability
- Velero availability
- optional jq availability

A typical troubleshooting sequence is:

```bash
lkoc doctor
kubectl config current-context
kubectl cluster-info
kubectl get nodes
kubectl get pods -A
```

---

# Common troubleshooting

## `kubectl` not found

```bash
command -v kubectl
```

Install kubectl through the installation method supported by your Kubernetes platform or Linux distribution.

## No contexts

```bash
kubectl config get-contexts
echo "$KUBECONFIG"
```

Check the default `~/.kube/config` as well.

## `Forbidden`

A Kubernetes error such as:

```text
Error from server (Forbidden)
```

usually means the selected identity lacks RBAC permissions.

Check:

```bash
kubectl auth can-i --list
```

## TLS / certificate failures

Verify kubeconfig server and CA configuration. LKOC does not silently disable Kubernetes TLS validation.

## Helm screen empty

```bash
helm version
helm list -A
```

## Velero unavailable

```bash
velero version
velero backup-location get
```

## Terminal layout problems

```bash
tput cols
tput lines
echo "$TERM"
```

Use UTF-8 and preferably:

```text
TERM=xterm-256color
>= 120 columns
```

---

# CLI reference

```text
lkoc
lkoc tui
lkoc --version
lkoc doctor
lkoc contexts

lkoc [--context CONTEXT] get nodes
lkoc [--context CONTEXT] get pods
lkoc [--context CONTEXT] get namespaces
lkoc [--context CONTEXT] get events
lkoc [--context CONTEXT] get deployments
lkoc [--context CONTEXT] get statefulsets
lkoc [--context CONTEXT] get daemonsets
lkoc [--context CONTEXT] get services
lkoc [--context CONTEXT] get ingresses
lkoc [--context CONTEXT] get pvcs

lkoc --context CONTEXT logs NAMESPACE POD --tail 200
lkoc --context CONTEXT scale NAMESPACE DEPLOYMENT REPLICAS
lkoc --context CONTEXT restart NAMESPACE DEPLOYMENT
lkoc --context CONTEXT apply MANIFEST
```

A dedicated reference is also available in [docs/CLI_REFERENCE.md](docs/CLI_REFERENCE.md).

---

# Project structure

```text
Linux-Kubernetes-Operations-Center-advanced/
├── .github/
│   └── workflows/
│       └── ci.yml
├── bin/
│   └── lkoc
├── docs/
│   ├── CLI_REFERENCE.md
│   ├── MANUAL.md
│   └── TROUBLESHOOTING.md
├── lkoc/
│   ├── __init__.py
│   ├── ansi.py
│   ├── cli.py
│   ├── core.py
│   ├── dashboard.py
│   ├── doctor.py
│   └── kube.py
├── tests/
│   ├── test_ansi.py
│   └── test_core.py
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── SECURITY.md
├── install.sh
└── uninstall.sh
```

---

# Development and tests

Compile:

```bash
python3 -m compileall -q lkoc
```

Run tests:

```bash
PYTHONPATH=. python3 -m unittest discover -s tests -v
```

Check shell syntax:

```bash
bash -n install.sh
bash -n uninstall.sh
```

CLI smoke test:

```bash
PYTHONPATH=. python3 -m lkoc.cli --version
```

The test suite includes an ANSI alignment regression test: after terminal color escape sequences are removed, every rendered frame line must have the same visible width.

GitHub Actions runs compile, unit tests, shell syntax checks and a CLI smoke test on pushes and pull requests.

---

# Uninstall

From the repository:

```bash
sudo ./uninstall.sh
```

The uninstaller removes:

```text
/usr/local/bin/lkoc
/opt/lkoc
```

It does **not** remove kubeconfig and does not delete Kubernetes resources.

---

# Current design boundaries

Version 1.0.0 is an operational Kubernetes console, not a replacement for every Kubernetes ecosystem component.

It intentionally relies on established tools where appropriate:

- `kubectl` for Kubernetes API operations
- `helm` for Helm inventory
- `velero` for Kubernetes-aware backup/restore

It does not currently provide:

- an in-cluster agent
- a web dashboard
- Prometheus metric ingestion
- Alertmanager integration
- a manifest editor
- a NetworkPolicy editor
- automated cluster upgrades
- secret-value browsing

Those can be added as isolated modules without changing the base TUI architecture.

---

# Production note

Test state-changing operations against a non-production cluster before using them in critical environments.

A healthy LKOC dashboard indicates the Kubernetes state visible through the selected identity. It is not by itself proof of application availability or recoverability.

For production clusters, combine LKOC with:

- Kubernetes-native monitoring
- centralized logs
- tested backups
- RBAC
- change control
- external availability monitoring
- documented disaster-recovery procedures

---

# Documentation

Additional documentation:

- [Administrator Manual](docs/MANUAL.md)
- [CLI Reference](docs/CLI_REFERENCE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Security Policy](SECURITY.md)
- [Contributing](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)

---

# License

MIT License. See [LICENSE](LICENSE).

---

# Author

**Antonios Mortos**

**Designed and Development by : antonios.mortos@outlook.com**
