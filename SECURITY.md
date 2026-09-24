# Security Policy

Linux Kubernetes Operations Center - Advanced operates with the same Kubernetes credentials and RBAC permissions available to `kubectl` for the selected context.

## Reporting a vulnerability

Please report security issues privately to:

**antonios.mortos@outlook.com**

Include the affected version, Kubernetes distribution/version, reproduction steps and expected impact. Remove credentials, tokens, certificates and customer data from logs before sending them.

## Security guidance

- Protect kubeconfig files and private keys.
- Use least-privilege RBAC.
- Keep production and non-production contexts clearly separated.
- Review manifest content before `apply`.
- Treat scale/restart/restore operations as production changes.
- Use short-lived credentials where supported.
- Audit cluster-admin access.
- Keep backup credentials and Velero storage permissions appropriately restricted.

**Designed and Development by : antonios.mortos@outlook.com**
