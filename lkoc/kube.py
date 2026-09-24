from __future__ import annotations
import json
from dataclasses import dataclass
from .core import run,run_json,which
@dataclass
class KubeClient:
    context:str|None=None
    def _base(self):return ["kubectl"]+(["--context",self.context] if self.context else [])
    def contexts(self):
        data=run_json(["kubectl","config","view","-o","json"]);cur=data.get("current-context","");out=[]
        for x in data.get("contexts",[]):
            c=x.get("context",{});out.append({"name":x.get("name",""),"cluster":c.get("cluster",""),"user":c.get("user",""),"namespace":c.get("namespace","default"),"current":x.get("name","")==cur})
        return out
    def current_context(self):
        cp=run(["kubectl","config","current-context"],check=False);return cp.stdout.strip() if cp.returncode==0 else ""
    def get(self,res,*,all_namespaces=False):
        cmd=self._base()+["get",res]+(["-A"] if all_namespaces else [])+["-o","json"];return run_json(cmd)
    def nodes(self):
        out=[]
        for i in self.get("nodes").get("items",[]):
            m=i.get("metadata",{});s=i.get("status",{});cond={c.get("type"):c for c in s.get("conditions",[])};ready=cond.get("Ready",{}).get("status")=="True";roles=[]
            for k in m.get("labels",{}):
                p="node-role.kubernetes.io/"
                if k.startswith(p):roles.append(k[len(p):] or "worker")
            a=s.get("allocatable",{});info=s.get("nodeInfo",{});out.append({"name":m.get("name",""),"status":"READY" if ready else "NOTREADY","roles":",".join(roles) or "worker","cpu":a.get("cpu",""),"memory":a.get("memory",""),"pods":a.get("pods",""),"os":info.get("osImage","")})
        return out
    def namespaces(self):return [{"name":i.get("metadata",{}).get("name",""),"status":i.get("status",{}).get("phase","")} for i in self.get("namespaces").get("items",[])]
    def pods(self):
        out=[]
        for i in self.get("pods",all_namespaces=True).get("items",[]):
            m=i.get("metadata",{});s=i.get("status",{});spec=i.get("spec",{});cs=s.get("containerStatuses",[]);restarts=sum(int(x.get("restartCount",0)) for x in cs);ready=sum(1 for x in cs if x.get("ready"));reason=""
            for x in cs:
                w=(x.get("state") or {}).get("waiting")
                if w and w.get("reason"):reason=w["reason"];break
            out.append({"namespace":m.get("namespace",""),"name":m.get("name",""),"ready":f"{ready}/{len(cs)}","status":str(reason or s.get("phase","Unknown")).upper(),"restarts":restarts,"node":spec.get("nodeName","")})
        return out
    def workloads(self,kind):
        out=[]
        for i in self.get(kind,all_namespaces=True).get("items",[]):
            m=i.get("metadata",{});spec=i.get("spec",{});s=i.get("status",{});desired=spec.get("replicas",1);ready=s.get("readyReplicas",s.get("numberReady",0)) or 0;avail=s.get("availableReplicas",ready) or 0;out.append({"namespace":m.get("namespace",""),"name":m.get("name",""),"desired":desired,"ready":ready,"available":avail,"status":"HEALTHY" if desired==ready else "DEGRADED"})
        return out
    def services(self):
        out=[]
        for i in self.get("services",all_namespaces=True).get("items",[]):
            m=i.get("metadata",{});s=i.get("spec",{});out.append({"namespace":m.get("namespace",""),"name":m.get("name",""),"type":s.get("type",""),"clusterIP":s.get("clusterIP",""),"ports":",".join(str(p.get("port","")) for p in s.get("ports",[]))})
        return out
    def ingresses(self):
        out=[]
        for i in self.get("ingresses.networking.k8s.io",all_namespaces=True).get("items",[]):
            m=i.get("metadata",{});s=i.get("spec",{});out.append({"namespace":m.get("namespace",""),"name":m.get("name",""),"class":s.get("ingressClassName",""),"hosts":",".join(r.get("host","") for r in s.get("rules",[]) if r.get("host"))})
        return out
    def pvcs(self):
        out=[]
        for i in self.get("pvc",all_namespaces=True).get("items",[]):
            m=i.get("metadata",{});sp=i.get("spec",{});st=i.get("status",{});out.append({"namespace":m.get("namespace",""),"name":m.get("name",""),"storageClass":sp.get("storageClassName",""),"capacity":(st.get("capacity") or {}).get("storage",""),"status":st.get("phase","")})
        return out
    def storageclasses(self):
        return [{"name":i.get("metadata",{}).get("name",""),"provisioner":i.get("provisioner",""),"reclaimPolicy":i.get("reclaimPolicy",""),"volumeBindingMode":i.get("volumeBindingMode","")} for i in self.get("storageclass.storage.k8s.io").get("items",[])]
    def events(self,limit=50):
        rows=[]
        for i in self.get("events",all_namespaces=True).get("items",[]):
            m=i.get("metadata",{});o=i.get("involvedObject",{});rows.append({"namespace":m.get("namespace",""),"type":i.get("type",""),"reason":i.get("reason",""),"object":f'{o.get("kind","")}/{o.get("name","")}',"message":i.get("message",""),"time":i.get("lastTimestamp") or i.get("eventTime") or m.get("creationTimestamp","")})
        rows.sort(key=lambda x:x["time"],reverse=True);return rows[:limit]
    def logs(self,ns,pod,tail=200):return run(self._base()+["-n",ns,"logs",pod,"--tail",str(tail)],check=False).stdout
    def scale(self,ns,name,repl):return run(self._base()+["-n",ns,"scale","deployment",name,"--replicas",str(repl)]).stdout.strip()
    def rollout_restart(self,ns,name):return run(self._base()+["-n",ns,"rollout","restart",f"deployment/{name}"]).stdout.strip()
    def apply(self,path):return run(self._base()+["apply","-f",path]).stdout.strip()
class HelmClient:
    def __init__(self,context=None):self.context=context
    def releases(self):
        if not which("helm"):return []
        cmd=["helm","list","-A","-o","json"]+(["--kube-context",self.context] if self.context else []);cp=run(cmd,check=False)
        try:return json.loads(cp.stdout) if cp.returncode==0 else []
        except:return []
class VeleroClient:
    def __init__(self,context=None):self.context=context
    def _base(self):return ["velero"]+(["--kubecontext",self.context] if self.context else [])
    def available(self):return bool(which("velero"))
    def backups(self):
        if not self.available():return []
        cp=run(self._base()+["backup","get","-o","json"],check=False)
        try:return json.loads(cp.stdout).get("items",[]) if cp.returncode==0 else []
        except:return []
    def create_backup(self,name,namespaces=None):
        cmd=self._base()+["backup","create",name]
        if namespaces:cmd += ["--include-namespaces",",".join(namespaces)]
        return run(cmd).stdout.strip()
    def create_restore(self,name,backup):return run(self._base()+["restore","create",name,"--from-backup",backup]).stdout.strip()
