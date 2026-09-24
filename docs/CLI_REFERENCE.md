# CLI Reference

```bash
lkoc
lkoc tui
lkoc --version
lkoc doctor
lkoc contexts
```

Read-only:

```bash
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
```

Actions:

```bash
lkoc --context CONTEXT scale NAMESPACE DEPLOYMENT REPLICAS
lkoc --context CONTEXT restart NAMESPACE DEPLOYMENT
lkoc --context CONTEXT apply FILE
lkoc --context CONTEXT logs NAMESPACE POD --tail 200
```

Designed and Development by : antonios.mortos@outlook.com
