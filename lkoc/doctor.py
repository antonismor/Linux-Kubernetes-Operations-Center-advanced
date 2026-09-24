import os,platform
from .core import which

def report():
    tools=[("kubectl",True,"Kubernetes client"),("helm",False,"Helm release management"),("velero",False,"Cluster backup/restore"),("jq",False,"Optional JSON utility")]
    return {"platform":platform.platform(),"python":platform.python_version(),"kubeconfig":os.getenv("KUBECONFIG",os.path.expanduser("~/.kube/config")),"tools":[{"name":n,"required":r,"description":d,"ok":bool(which(n)),"path":which(n) or ""} for n,r,d in tools]}
