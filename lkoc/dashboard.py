from .ansi import status,table_row

def cluster_dashboard(c):
    lines=[]
    try:
        nodes=c.nodes();pods=c.pods();nss=c.namespaces();deps=c.workloads("deployments.apps");bad=[p for p in pods if p["status"] not in {"RUNNING","SUCCEEDED"}];nr=[n for n in nodes if n["status"]!="READY"];health="HEALTHY" if not bad and not nr else "WARNING"
        lines.append(table_row(["CONTEXT","NODES","PODS","NAMESPACES","DEPLOYMENTS","HEALTH"],[26,9,9,13,13,18]));lines.append("  "+"─"*100);lines.append(table_row([c.context or c.current_context(),len(nodes),len(pods),len(nss),len(deps),status(health)],[26,9,9,13,13,18]))
        if bad:lines.append(f"  {len(bad)} pod(s) require attention.")
        if nr:lines.append(f"  {len(nr)} node(s) are not Ready.")
    except Exception as e:lines.append(f"  Cluster data unavailable: {e}")
    return lines
