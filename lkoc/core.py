from __future__ import annotations
import json, os, re, shlex, shutil, subprocess
from pathlib import Path
from typing import Any
APP_NAME="LINUX KUBERNETES OPERATIONS CENTER - ADVANCED"
AUTHOR="Designed and Development by : antonios.mortos@outlook.com"
CONFIG_DIR=Path(os.getenv("LKOC_CONFIG",Path.home()/".config"/"lkoc"))
STATE_DIR=Path(os.getenv("LKOC_STATE",Path.home()/".local"/"state"/"lkoc"))
LOG_DIR=Path(os.getenv("LKOC_LOG",STATE_DIR/"logs"))
def ensure_dirs():
    for p in (CONFIG_DIR,STATE_DIR,LOG_DIR): p.mkdir(parents=True,exist_ok=True)
def which(name): return shutil.which(name)
def run(cmd,*,check=True,capture=True,timeout=60,env=None):
    if isinstance(cmd,str): cmd=shlex.split(cmd)
    cp=subprocess.run(cmd,text=True,capture_output=capture,timeout=timeout,env=env)
    if check and cp.returncode!=0:
        raise RuntimeError(f"Command failed ({cp.returncode}): {' '.join(cmd)}\n{(cp.stderr or cp.stdout or '').strip()}")
    return cp
def run_json(cmd,*,timeout=60):
    cp=run(cmd,timeout=timeout)
    try:return json.loads(cp.stdout)
    except json.JSONDecodeError as e: raise RuntimeError(f"Invalid JSON from command: {' '.join(cmd)}") from e
def safe_name(value,limit=80):
    value=re.sub(r"[^A-Za-z0-9._-]+","-",value.strip()); return value.strip("-")[:limit]
def parse_quantity(value):
    if value is None:return 0.0
    if isinstance(value,(int,float)):return float(value)
    s=str(value).strip()
    if s.endswith("m") and s[:-1].replace(".","",1).isdigit(): return float(s[:-1])/1000.0
    suffixes={"Ki":1024,"Mi":1024**2,"Gi":1024**3,"Ti":1024**4,"Pi":1024**5,"K":1000,"M":1000**2,"G":1000**3,"T":1000**4}
    for suf,mult in suffixes.items():
        if s.endswith(suf): return float(s[:-len(suf)])*mult
    try:return float(s)
    except:return 0.0
