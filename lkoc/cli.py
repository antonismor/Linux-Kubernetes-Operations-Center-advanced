from __future__ import annotations
import argparse,json,sys
from pathlib import Path
from . import __version__
from .ansi import Screen,menu,status,table_row,GREEN,RED,YELLOW,RESET
from .core import APP_NAME,ensure_dirs,which
from .dashboard import cluster_dashboard
from .doctor import report as doctor_report
from .kube import KubeClient,HelmClient,VeleroClient
MAIN=["Dashboard","Clusters / Contexts","Nodes","Namespaces","Pods","Deployments","StatefulSets","DaemonSets","Services","Ingress","Storage (PVC / StorageClasses)","Helm Releases","Recent Events","Logs","Scale Deployment","Rollout Restart","Apply Manifest","Backup & Restore (Velero)","Security & RBAC","Network Policies","Jobs & CronJobs","Alerts","Doctor / Diagnostics","Exit"]
def show_text(title,lines,context=""):
    s=Screen();s.clear();s.header(context=context,version=__version__);s.section(title)
    for line in lines:s.section_row(line)
    s.section_end();s.footer();input("\nPress ENTER to continue...")
def choose(items,title,formatter=lambda x:str(x),context=""):
    labels=[formatter(x) for x in items]+["Back"];idx=menu(labels,title=title,context=context,version=__version__);return None if idx is None or idx>=len(items) else items[idx]
def lines_nodes(c):
    out=[table_row(["NAME","STATUS","ROLE","CPU","MEMORY","PODS","OS"],[26,14,20,7,14,7,26]),"  "+"─"*120]
    for n in c.nodes():out.append(table_row([n["name"],status(n["status"]),n["roles"],n["cpu"],n["memory"],n["pods"],n["os"]],[26,14,20,7,14,7,26]))
    return out
def lines_namespaces(c):return [table_row(["NAME","STATUS"],[45,18]),"  "+"─"*66]+[table_row([x["name"],status(x["status"])],[45,18]) for x in c.namespaces()]
def lines_pods(c):
    out=[table_row(["NAMESPACE","POD","READY","STATUS","RESTARTS","NODE"],[20,38,8,20,10,28]),"  "+"─"*132]
    for p in c.pods()[:80]:out.append(table_row([p["namespace"],p["name"],p["ready"],status(p["status"]),p["restarts"],p["node"]],[20,38,8,20,10,28]))
    return out
def lines_workloads(c,kind):
    out=[table_row(["NAMESPACE","NAME","DESIRED","READY","AVAILABLE","STATUS"],[20,40,9,9,11,18]),"  "+"─"*115]
    for x in c.workloads(kind):out.append(table_row([x["namespace"],x["name"],x["desired"],x["ready"],x["available"],status(x["status"])],[20,40,9,9,11,18]))
    return out
def lines_services(c):
    out=[table_row(["NAMESPACE","SERVICE","TYPE","CLUSTER IP","PORTS"],[20,34,18,20,25]),"  "+"─"*120]
    for x in c.services():out.append(table_row([x["namespace"],x["name"],x["type"],x["clusterIP"],x["ports"]],[20,34,18,20,25]))
    return out
def lines_ingress(c):
    out=[table_row(["NAMESPACE","INGRESS","CLASS","HOSTS"],[20,34,18,55]),"  "+"─"*132]
    for x in c.ingresses():out.append(table_row([x["namespace"],x["name"],x["class"],x["hosts"]],[20,34,18,55]))
    return out
def lines_storage(c):
    out=["PVCs",table_row(["NAMESPACE","PVC","STORAGE CLASS","CAPACITY","STATUS"],[20,32,28,14,16]),"  "+"─"*118]
    for x in c.pvcs():out.append(table_row([x["namespace"],x["name"],x["storageClass"],x["capacity"],status(x["status"])],[20,32,28,14,16]))
    out += ["","StorageClasses",table_row(["NAME","PROVISIONER","RECLAIM","BINDING"],[30,48,16,24]),"  "+"─"*124]
    for x in c.storageclasses():out.append(table_row([x["name"],x["provisioner"],x["reclaimPolicy"],x["volumeBindingMode"]],[30,48,16,24]))
    return out
def lines_events(c):
    out=[table_row(["TIME","TYPE","NAMESPACE","OBJECT","REASON","MESSAGE"],[20,10,18,30,22,50]),"  "+"─"*154]
    for x in c.events(60):out.append(table_row([x["time"],status("WARNING" if x["type"]=="Warning" else "ACTIVE"),x["namespace"],x["object"],x["reason"],x["message"]],[20,10,18,30,22,50]))
    return out
def lines_helm(ctx):
    rows=HelmClient(ctx).releases()
    if not rows:return ["Helm is not installed, no releases exist, or the context cannot be queried."]
    out=[table_row(["NAME","NAMESPACE","REVISION","STATUS","CHART","APP VERSION"],[28,20,10,16,36,16]),"  "+"─"*134]
    for x in rows:out.append(table_row([x.get("name",""),x.get("namespace",""),x.get("revision",""),status(x.get("status","")),x.get("chart",""),x.get("app_version","")],[28,20,10,16,36,16]))
    return out
def lines_jobs(c):
    out=["Jobs",table_row(["NAMESPACE","NAME","SUCCEEDED","FAILED","ACTIVE"],[20,42,12,10,10]),"  "+"─"*100]
    for i in c.get("jobs.batch",all_namespaces=True).get("items",[]):
        m=i.get("metadata",{});s=i.get("status",{});out.append(table_row([m.get("namespace",""),m.get("name",""),s.get("succeeded",0),s.get("failed",0),s.get("active",0)],[20,42,12,10,10]))
    out += ["","CronJobs",table_row(["NAMESPACE","NAME","SCHEDULE","SUSPEND"],[20,42,30,10]),"  "+"─"*108]
    for i in c.get("cronjobs.batch",all_namespaces=True).get("items",[]):
        m=i.get("metadata",{});s=i.get("spec",{});out.append(table_row([m.get("namespace",""),m.get("name",""),s.get("schedule",""),str(s.get("suspend",False))],[20,42,30,10]))
    return out
def lines_rbac(c):
    cr=c.get("clusterroles.rbac.authorization.k8s.io");cb=c.get("clusterrolebindings.rbac.authorization.k8s.io");r=c.get("roles.rbac.authorization.k8s.io",all_namespaces=True);rb=c.get("rolebindings.rbac.authorization.k8s.io",all_namespaces=True);return [f"ClusterRoles: {len(cr.get('items',[]))}",f"ClusterRoleBindings: {len(cb.get('items',[]))}",f"Namespaced Roles: {len(r.get('items',[]))}",f"Namespaced RoleBindings: {len(rb.get('items',[]))}"]
def lines_netpol(c):
    out=[table_row(["NAMESPACE","NAME","POD SELECTOR","POLICY TYPES"],[24,40,48,28]),"  "+"─"*146]
    for i in c.get("networkpolicies.networking.k8s.io",all_namespaces=True).get("items",[]):
        m=i.get("metadata",{});s=i.get("spec",{});sel=json.dumps((s.get("podSelector") or {}).get("matchLabels",{}),separators=(",",":"));out.append(table_row([m.get("namespace",""),m.get("name",""),sel,",".join(s.get("policyTypes",[]))],[24,40,48,28]))
    return out
def lines_alerts(c):
    a=[]
    for p in c.pods():
        if p["status"] not in {"RUNNING","SUCCEEDED"}:a.append(("POD",p["namespace"],p["name"],p["status"]))
    for e in c.events(100):
        if e["type"]=="Warning":a.append(("EVENT",e["namespace"],e["object"],e["reason"]))
    out=[table_row(["TYPE","NAMESPACE","OBJECT","DETAIL"],[12,22,45,55]),"  "+"─"*140]
    for x in a[:80]:out.append(table_row(x,[12,22,45,55]))
    if not a:out.append("  No active warnings detected.")
    return out
def choose_deploy(c):return choose(c.workloads("deployments.apps"),"SELECT DEPLOYMENT",lambda x:f'{x["namespace"]}/{x["name"]}  {x["ready"]}/{x["desired"]}',c.context or "")
def action_logs(c):
    p=choose(c.pods(),"SELECT POD",lambda x:f'{x["namespace"]}/{x["name"]}  {x["status"]}',c.context or "")
    if p:show_text(f'LOGS {p["namespace"]}/{p["name"]}',c.logs(p["namespace"],p["name"],200).splitlines()[-120:],c.context or "")
def action_scale(c):
    d=choose_deploy(c)
    if not d:return
    r=input("Replicas: ").strip()
    if r.isdigit():show_text("SCALE RESULT",[c.scale(d["namespace"],d["name"],int(r))],c.context or "")
def action_restart(c):
    d=choose_deploy(c)
    if d and input(f'Restart {d["namespace"]}/{d["name"]}? Type YES: ').strip()=="YES":show_text("ROLLOUT RESTART",[c.rollout_restart(d["namespace"],d["name"])],c.context or "")
def action_apply(c):
    p=input("Manifest path: ").strip()
    if p and Path(p).exists() and input(f"Apply {p}? Type APPLY: ").strip()=="APPLY":show_text("APPLY RESULT",c.apply(p).splitlines(),c.context or "")
def action_velero(c):
    v=VeleroClient(c.context)
    if not v.available():return show_text("VELERO",["Velero CLI is not installed/configured."],c.context or "")
    acts=["List Backups","Create Backup","Create Restore","Back"];i=menu(acts,title="BACKUP & RESTORE",context=c.context or "",version=__version__)
    if i is None or acts[i]=="Back":return
    if acts[i]=="List Backups":
        out=[table_row(["NAME","PHASE","CREATED"],[50,20,30]),"  "+"─"*104]
        for x in v.backups():
            m=x.get("metadata",{});s=x.get("status",{});out.append(table_row([m.get("name",""),status(s.get("phase","")),m.get("creationTimestamp","")],[50,20,30]))
        return show_text("VELERO BACKUPS",out,c.context or "")
    if acts[i]=="Create Backup":
        n=input("Backup name: ").strip();ns=input("Namespaces comma-separated (blank=all): ").strip()
        if n and input(f"Create backup {n}? Type BACKUP: ").strip()=="BACKUP":show_text("VELERO BACKUP",[v.create_backup(n,[x.strip() for x in ns.split(",") if x.strip()] if ns else None)],c.context or "")
    if acts[i]=="Create Restore":
        b=input("Source backup name: ").strip();n=input("Restore name: ").strip()
        if b and n and input(f"Restore {b}? Type RESTORE: ").strip()=="RESTORE":show_text("VELERO RESTORE",[v.create_restore(n,b)],c.context or "")
def tui():
    if not which("kubectl"):return show_text("DEPENDENCY ERROR",["kubectl was not found in PATH.","Install kubectl and configure kubeconfig first."])
    context=KubeClient().current_context()
    while True:
        c=KubeClient(context);i=menu(MAIN,title="MAIN MENU",context=f"Current cluster context: {context or '(none)'}",dashboard=cluster_dashboard(c),version=__version__)
        if i is None or MAIN[i]=="Exit":print(RESET);return
        x=MAIN[i]
        try:
            if x=="Dashboard":show_text("CLUSTER DASHBOARD",cluster_dashboard(c),context)
            elif x=="Clusters / Contexts":
                s=choose(c.contexts(),"SELECT KUBERNETES CONTEXT",lambda a:("* " if a["current"] else "  ")+a["name"],context)
                if s:context=s["name"]
            elif x=="Nodes":show_text("NODES",lines_nodes(c),context)
            elif x=="Namespaces":show_text("NAMESPACES",lines_namespaces(c),context)
            elif x=="Pods":show_text("PODS",lines_pods(c),context)
            elif x=="Deployments":show_text("DEPLOYMENTS",lines_workloads(c,"deployments.apps"),context)
            elif x=="StatefulSets":show_text("STATEFULSETS",lines_workloads(c,"statefulsets.apps"),context)
            elif x=="DaemonSets":show_text("DAEMONSETS",lines_workloads(c,"daemonsets.apps"),context)
            elif x=="Services":show_text("SERVICES",lines_services(c),context)
            elif x=="Ingress":show_text("INGRESS",lines_ingress(c),context)
            elif x=="Storage (PVC / StorageClasses)":show_text("STORAGE",lines_storage(c),context)
            elif x=="Helm Releases":show_text("HELM RELEASES",lines_helm(context),context)
            elif x=="Recent Events":show_text("RECENT EVENTS",lines_events(c),context)
            elif x=="Logs":action_logs(c)
            elif x=="Scale Deployment":action_scale(c)
            elif x=="Rollout Restart":action_restart(c)
            elif x=="Apply Manifest":action_apply(c)
            elif x=="Backup & Restore (Velero)":action_velero(c)
            elif x=="Security & RBAC":show_text("SECURITY & RBAC",lines_rbac(c),context)
            elif x=="Network Policies":show_text("NETWORK POLICIES",lines_netpol(c),context)
            elif x=="Jobs & CronJobs":show_text("JOBS & CRONJOBS",lines_jobs(c),context)
            elif x=="Alerts":show_text("ALERTS",lines_alerts(c),context)
            elif x=="Doctor / Diagnostics":
                d=doctor_report();lines=[f"Platform: {d['platform']}",f"Python: {d['python']}",f"Kubeconfig: {d['kubeconfig']}",""]
                for t in d["tools"]:lines.append(f"  {GREEN+'✓'+RESET if t['ok'] else (RED+'✗'+RESET if t['required'] else YELLOW+'!'+RESET)} {t['name']:<10} {t['description']}")
                show_text("DOCTOR / DIAGNOSTICS",lines,context)
        except Exception as e:show_text("ERROR",str(e).splitlines(),context)
def build_parser():
    p=argparse.ArgumentParser(prog="lkoc",description=APP_NAME);p.add_argument("--version",action="version",version=f"%(prog)s {__version__}");p.add_argument("--context");s=p.add_subparsers(dest="cmd");s.add_parser("tui");s.add_parser("contexts");g=s.add_parser("get");g.add_argument("kind",choices=["nodes","pods","namespaces","events","deployments","statefulsets","daemonsets","services","ingresses","pvcs"]);a=s.add_parser("scale");a.add_argument("namespace");a.add_argument("deployment");a.add_argument("replicas",type=int);a=s.add_parser("restart");a.add_argument("namespace");a.add_argument("deployment");a=s.add_parser("apply");a.add_argument("path");a=s.add_parser("logs");a.add_argument("namespace");a.add_argument("pod");a.add_argument("--tail",type=int,default=200);s.add_parser("doctor");return p
def main(argv=None):
    p=build_parser();a=p.parse_args(argv);ensure_dirs()
    if not a.cmd or a.cmd=="tui":return tui()
    if a.cmd=="contexts":print(json.dumps(KubeClient().contexts(),indent=2));return
    c=KubeClient(a.context)
    if a.cmd=="get":
        f={"nodes":c.nodes,"pods":c.pods,"namespaces":c.namespaces,"events":c.events,"deployments":lambda:c.workloads("deployments.apps"),"statefulsets":lambda:c.workloads("statefulsets.apps"),"daemonsets":lambda:c.workloads("daemonsets.apps"),"services":c.services,"ingresses":c.ingresses,"pvcs":c.pvcs}[a.kind];print(json.dumps(f(),indent=2));return
    if a.cmd=="scale":print(c.scale(a.namespace,a.deployment,a.replicas));return
    if a.cmd=="restart":print(c.rollout_restart(a.namespace,a.deployment));return
    if a.cmd=="apply":print(c.apply(a.path));return
    if a.cmd=="logs":print(c.logs(a.namespace,a.pod,a.tail));return
    if a.cmd=="doctor":print(json.dumps(doctor_report(),indent=2));return
if __name__=="__main__":
    try:main()
    except KeyboardInterrupt:print("\nCancelled.",file=sys.stderr);raise SystemExit(130)
    except Exception as e:print(f"ERROR: {e}",file=sys.stderr);raise SystemExit(1)
