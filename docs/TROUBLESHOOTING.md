# Troubleshooting

## Diagnostics

```bash
lkoc doctor
```

## kubectl missing

```bash
command -v kubectl
```

Install kubectl using the supported installation method for your Kubernetes platform/distribution.

## No cluster contexts

```bash
kubectl config get-contexts
echo "$KUBECONFIG"
```

## RBAC Forbidden

```bash
kubectl auth can-i --list
kubectl auth can-i list pods -A
```

## Helm view empty

```bash
helm version
helm list -A
```

## Velero unavailable

```bash
velero version
velero backup-location get
```

## Terminal alignment

```bash
tput cols
tput lines
echo "$TERM"
```

Use a UTF-8 terminal, preferably `xterm-256color`, at least 120 columns wide.

Designed and Development by : antonios.mortos@outlook.com
