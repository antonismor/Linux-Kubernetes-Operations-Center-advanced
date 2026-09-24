# Contributing

Contributions are welcome.

Before submitting changes, run:

```bash
python3 -m compileall -q lkoc
PYTHONPATH=. python3 -m unittest discover -s tests -v
bash -n install.sh
bash -n uninstall.sh
```

Please preserve these design principles:

- terminal frames must remain aligned with ANSI colors enabled;
- read-only operations should remain the default;
- state-changing actions should be obvious and deliberate;
- never print kubeconfig tokens, client keys or secret data;
- Kubernetes RBAC must remain authoritative;
- new features should work with standard Kubernetes APIs or clearly documented optional tooling;
- add tests for parsing or rendering changes where practical.

**Designed and Development by : antonios.mortos@outlook.com**
