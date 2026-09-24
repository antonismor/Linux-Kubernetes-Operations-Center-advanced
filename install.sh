#!/usr/bin/env bash
set -euo pipefail
[[ ${EUID:-$(id -u)} -eq 0 ]] || { echo "Run installer with sudo."; exit 1; }
ROOT="$(cd "$(dirname "$0")" && pwd)"
echo "Installing Linux Kubernetes Operations Center - Advanced"
install -d -m 755 /opt/lkoc
rm -rf /opt/lkoc/lkoc
cp -a "$ROOT/lkoc" /opt/lkoc/
cat >/usr/local/bin/lkoc <<'WRAP'
#!/usr/bin/env bash
export PYTHONPATH="/opt/lkoc${PYTHONPATH:+:$PYTHONPATH}"
exec python3 -m lkoc.cli "$@"
WRAP
chmod 755 /usr/local/bin/lkoc
echo
command -v kubectl >/dev/null 2>&1 || echo "WARNING: kubectl is not installed. Install it before using cluster features."
echo "Installed. Start with: lkoc"
/usr/local/bin/lkoc --version
