from __future__ import annotations
import os,re,sys,shutil,termios,tty
from datetime import datetime
from .core import APP_NAME,AUTHOR
ESC="\033[";RESET=ESC+"0m";BOLD=ESC+"1m";DIM=ESC+"2m";CYAN=ESC+"38;5;51m";BLUE=ESC+"38;5;39m";GREEN=ESC+"38;5;46m";YELLOW=ESC+"38;5;220m";RED=ESC+"38;5;196m";PURPLE=ESC+"38;5;141m";GRAY=ESC+"38;5;245m";WHITE=ESC+"38;5;255m";BG_SELECTED=ESC+"48;5;24m";FG_SELECTED=ESC+"38;5;231m"
ANSI_RE=re.compile(r"\x1b\[[0-9;]*m")
def visible_len(v):return len(ANSI_RE.sub("",str(v)))
def clip(v,w):
    v=str(v);raw=ANSI_RE.sub("",v)
    if len(raw)<=w:return v
    if w<=0:return ""
    return raw[:max(0,w-1)]+"…"
def pad(v,w,align="left"):
    v=clip(v,w);n=max(0,w-visible_len(v))
    if align=="right":return " "*n+v
    if align=="center":
        l=n//2;return " "*l+v+" "*(n-l)
    return v+" "*n
def status(text):
    t=str(text).upper()
    if t in {"ONLINE","RUNNING","READY","HEALTHY","ACTIVE","AVAILABLE","SUCCEEDED","SUCCESS","BOUND"}:return GREEN+"● "+t+RESET
    if t in {"FAILED","OFFLINE","ERROR","CRITICAL","NOTREADY","CRASHLOOPBACKOFF"}:return RED+"● "+t+RESET
    if t in {"WARNING","PENDING","TERMINATING","DEGRADED","UNKNOWN"}:return YELLOW+"● "+t+RESET
    return BLUE+"● "+t+RESET
def table_row(values,widths,aligns=None):
    aligns=aligns or ["left"]*len(values);return "  "+"  ".join(pad(v,w,a) for v,w,a in zip(values,widths,aligns))
class Screen:
    MAX_W=156;MIN_W=72
    def __init__(self):
        cols,rows=shutil.get_terminal_size((120,40));self.width=max(self.MIN_W,min(cols,self.MAX_W));self.inner=self.width-2;self.rows=rows
    def clear(self):sys.stdout.write("\033[2J\033[H");sys.stdout.flush()
    def top(self):print(CYAN+"╔"+"═"*self.inner+"╗"+RESET)
    def bottom(self):print(CYAN+"╚"+"═"*self.inner+"╝"+RESET)
    def divider(self):print(CYAN+"╠"+"═"*self.inner+"╣"+RESET)
    def line(self,text=""):print(CYAN+"║"+RESET+pad(text,self.inner)+CYAN+"║"+RESET)
    def header(self,context="",version=""):
        self.top();clock=datetime.now().strftime("%Y-%m-%d %H:%M:%S");title=" ◆ "+APP_NAME;right=(f"v{version}  "+clock) if version else clock;gap=max(1,self.inner-visible_len(title)-visible_len(right));self.line(BOLD+CYAN+title+RESET+" "*gap+DIM+right+RESET)
        if context:self.line("   "+DIM+context+RESET)
        self.divider()
    def section(self,title):
        title=f" {title} ";mid=max(0,self.inner-len(title)-3);print(CYAN+"║┌─"+title+"─"*mid+"┐║"+RESET)
    def section_row(self,text=""):print(CYAN+"║│"+RESET+pad(text,self.inner-2)+CYAN+"│║"+RESET)
    def section_end(self):print(CYAN+"║└"+"─"*(self.inner-2)+"┘║"+RESET)
    def footer(self,state="● READY"):
        self.divider();left=" ↑/↓ Navigate  ENTER Select  ESC Back  F1 Help  F5 Refresh";gap=max(1,self.inner-visible_len(left)-visible_len(state)-1);self.line(left+" "*gap+GREEN+state+RESET);self.line(" "+DIM+AUTHOR+RESET);self.bottom()
def read_key():
    if not sys.stdin.isatty():return input().strip()
    fd=sys.stdin.fileno();old=termios.tcgetattr(fd)
    try:
        tty.setraw(fd);ch=os.read(fd,1)
        if ch==b"\x1b":
            rest=os.read(fd,2)
            if rest==b"[A":return "UP"
            if rest==b"[B":return "DOWN"
            return "ESC"
        if ch in (b"\r",b"\n"):return "ENTER"
        if ch==b"\x03":raise KeyboardInterrupt
        return ch.decode(errors="ignore")
    finally:termios.tcsetattr(fd,termios.TCSADRAIN,old)
def menu(items,title="MAIN MENU",*,context="",dashboard=None,selected=0,version=""):
    s=Screen()
    while True:
        s.clear();s.header(context=context,version=version)
        if dashboard:
            s.section("DASHBOARD")
            for line in dashboard:s.section_row(line)
            s.section_end();s.line()
        s.section(title)
        for i,item in enumerate(items):
            label=f"  {'▶' if i==selected else ' '}  {item}"
            if i==selected:label=BG_SELECTED+FG_SELECTED+BOLD+pad(label,s.inner-2)+RESET
            s.section_row(label)
        s.section_end();s.footer();key=read_key()
        if key=="UP":selected=(selected-1)%len(items)
        elif key=="DOWN":selected=(selected+1)%len(items)
        elif key=="ENTER":return selected
        elif key in ("ESC","q","Q"):return None
