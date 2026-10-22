"""
Majestic AI v1.0 – Flask REST API Server (Part 1: core + intelligence routes)
Run: python server.py [--port PORT] [--debug]
"""
import os, sys, time, subprocess, threading, argparse, logging, json, shutil, uuid
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS

# ── Local modules ───────────────────────────────────────────────────────────
from visual_engine import print_banner, progress_bar, severity_card, tabular, HACKER_RED, GREEN, CYAN, GRAY, RESET, BOLD
from cache_engine import cache, procs, err_hist
from error_engine import ErrorType, MajesticError, classify_exception, GracefulDegradation
from agents import (IntelligentDecisionEngine, BugBountyWorkflowManager, BugBountyAgent,
                    CTFWorkflowManager, CTFAgent, CVEIntelligenceManager, AIExploitGenerator,
                    VulnerabilityCorrelator, TechnologyDetector, RateLimitDetector,
                    FailureRecoverySystem, PerformanceMonitor, ParameterOptimizer)
from browser_agent import HeadlessBrowserAgent

# ── Parse CLI args BEFORE Flask init ───────────────────────────────────────
parser = argparse.ArgumentParser(description="Majestic AI v1.0 API Server")
parser.add_argument("--port",  type=int, default=int(os.environ.get("HEXSTRIKE_PORT","8888")))
parser.add_argument("--debug", action="store_true")
args, _ = parser.parse_known_args()

# ── Logging setup ───────────────────────────────────────────────────────────
LOG_LEVEL = logging.DEBUG if args.debug else logging.INFO

class ColoredFormatter(logging.Formatter):
    EMOJIS = {logging.DEBUG:"🔍",logging.INFO:"✅",logging.WARNING:"⚠️",logging.ERROR:"❌",logging.CRITICAL:"🔥"}
    COLORS = {logging.DEBUG:GRAY,logging.INFO:GREEN,logging.WARNING:"\033[38;5;208m",
              logging.ERROR:HACKER_RED,logging.CRITICAL:"\033[38;5;196m"+"\033[1m"}
    def format(self, record):
        e = self.EMOJIS.get(record.levelno,"•")
        c = self.COLORS.get(record.levelno, "")
        msg = super().format(record)
        return f"{c}{e} {msg}{RESET}"

handler_console = logging.StreamHandler(sys.stdout)
handler_console.setFormatter(ColoredFormatter("%(asctime)s [%(name)s] %(message)s", "%H:%M:%S"))
handler_file    = logging.FileHandler("hexstrike.log", encoding="utf-8")
handler_file.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s – %(message)s"))

logging.basicConfig(level=LOG_LEVEL, handlers=[handler_console, handler_file])
logger = logging.getLogger("majestic")

# ── Flask app ───────────────────────────────────────────────────────────────
app = Flask(__name__)
CORS(app)

# ── Agent singletons ─────────────────────────────────────────────────────────
ide         = IntelligentDecisionEngine()
bb_manager  = BugBountyWorkflowManager()
bb_agent    = BugBountyAgent()
ctf_manager = CTFWorkflowManager()
ctf_agent   = CTFAgent()
cve_intel   = CVEIntelligenceManager()
exploit_gen = AIExploitGenerator()
vuln_corr   = VulnerabilityCorrelator()
tech_detect = TechnologyDetector()
rate_detect = RateLimitDetector()
fail_rec    = FailureRecoverySystem()
perf_mon    = PerformanceMonitor()
param_opt   = ParameterOptimizer()
browser     = HeadlessBrowserAgent()

# ── File storage ─────────────────────────────────────────────────────────────
FILE_DIR     = Path("/tmp/hexstrike_files")
FILE_DIR.mkdir(parents=True, exist_ok=True)
MAX_FILE_MB  = 100

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def ok(data, code=200):
    return jsonify({"status":"ok","data":data}), code

def err(msg, code=400, etype=None):
    err_hist.record(etype or "API_ERROR", msg, {"path": request.path})
    return jsonify({"status":"error","message":msg}), code

def run_cmd(cmd: str, timeout: int = 60) -> dict:
    key = f"cmd:{cmd}"
    cached = cache.get(key)
    if cached:
        return {**cached, "cached": True}
    t0 = time.time()
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        data = {
            "command":   cmd,
            "stdout":    result.stdout,
            "stderr":    result.stderr,
            "returncode":result.returncode,
            "duration":  round(time.time()-t0, 3),
            "cached":    False,
        }
        cache.set(key, data, ttl=300)
        perf_mon.record(cmd.split()[0], data["duration"], result.returncode == 0)
        return data
    except subprocess.TimeoutExpired:
        err_hist.record(ErrorType.TIMEOUT, f"Command timed out: {cmd}")
        return {"command":cmd,"error":"timeout","duration":timeout}
    except Exception as e:
        err_hist.record(classify_exception(e).value, str(e))
        return {"command":cmd,"error":str(e)}

# ─────────────────────────────────────────────────────────────────────────────
# CORE ROUTES
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return ok({"name":"Majestic AI v1.0","port":args.port,"status":"online",
                "endpoints":50,"agents":12,"tools":150})

@app.get("/health")
def health():
    return ok({"status":"healthy","uptime":time.time(),"cache":cache.stats(),
                "error_count":len(err_hist.recent(1000)),"version":"1.0.0"})

@app.get("/banner")
def banner():
    from visual_engine import BANNER
    return ok({"banner": BANNER, "ansi": True})

# ── Command execution ────────────────────────────────────────────────────────
@app.post("/execute")
def execute():
    body    = request.json or {}
    cmd     = body.get("command","")
    timeout = int(body.get("timeout", 60))
    if not cmd:
        return err("'command' is required")
    logger.info("🔧 Executing: %s", cmd)
    result = run_cmd(cmd, timeout)
    return ok(result)

@app.post("/execute/stream")
def execute_stream():
    body = request.json or {}
    cmd  = body.get("command","")
    if not cmd:
        return err("'command' is required")
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True)
    pid  = proc.pid
    procs.register(pid, {"command":cmd,"status":"running","started_at":time.time()})
    def reader():
        proc.wait()
        procs.update(pid, status="done", returncode=proc.returncode)
    threading.Thread(target=reader, daemon=True).start()
    return ok({"pid":pid,"command":cmd,"status":"running"})

# ── Process management ────────────────────────────────────────────────────────
@app.get("/processes")
def list_processes():
    return ok({"processes": procs.all()})

@app.get("/processes/<int:pid>")
def process_status(pid):
    p = procs.get(pid)
    if not p:
        return err(f"PID {pid} not found", 404)
    return ok(p)

@app.post("/processes/<int:pid>/pause")
def pause_process(pid):
    try:
        import psutil
        psutil.Process(pid).suspend()
        procs.update(pid, status="paused")
        return ok({"pid":pid,"action":"paused"})
    except Exception as e:
        return err(str(e))

@app.post("/processes/<int:pid>/resume")
def resume_process(pid):
    try:
        import psutil
        psutil.Process(pid).resume()
        procs.update(pid, status="running")
        return ok({"pid":pid,"action":"resumed"})
    except Exception as e:
        return err(str(e))

@app.post("/processes/<int:pid>/terminate")
def terminate_process(pid):
    try:
        import psutil
        psutil.Process(pid).terminate()
        procs.remove(pid)
        return ok({"pid":pid,"action":"terminated"})
    except Exception as e:
        return err(str(e))

@app.get("/processes/dashboard")
def process_dashboard():
    try:
        import psutil
        sys_procs = [{"pid":p.pid,"name":p.name(),"cpu":p.cpu_percent(),
                      "mem_mb":round(p.memory_info().rss/1024/1024,2),"status":p.status()}
                     for p in psutil.process_iter(["pid","name","cpu_percent","memory_info","status"])
                     if p.info["cpu_percent"] is not None][:50]
    except Exception:
        sys_procs = []
    return ok({"registered": procs.all(), "system_top50": sys_procs})

# ── Intelligence endpoints ────────────────────────────────────────────────────
@app.post("/intelligence/analyze-target")
def analyze_target():
    b = request.json or {}
    result = ide.analyze(
        b.get("target_type","web_app"),
        b.get("technologies",[]),
        b.get("objectives",[])
    )
    return ok(result)

@app.post("/intelligence/select-tools")
def select_tools():
    b = request.json or {}
    result = ide.analyze(b.get("target_type","web_app"), b.get("technologies",[]), [])
    return ok({"ranked_tools": result["ranked_tools"]})

@app.post("/intelligence/optimize-parameters")
def optimize_parameters():
    b   = request.json or {}
    tool = b.get("tool","nmap")
    return ok(param_opt.optimize(tool, b.get("context",{})))

@app.post("/intelligence/create-attack-chain")
def create_attack_chain():
    b = request.json or {}
    result = ide.analyze(b.get("target_type","web_app"),
                         b.get("technologies",[]),
                         b.get("objectives",["privilege_escalation"]))
    return ok({"attack_chains": result["attack_chains"]})

@app.post("/intelligence/smart-scan")
def smart_scan():
    b      = request.json or {}
    target = b.get("target","")
    if not target:
        return err("'target' is required")
    # detect tech from headers
    detected = tech_detect.detect(body=target)
    analysis = ide.analyze("web_app", detected, b.get("objectives",["RCE","SQLi"]))
    return ok({"target":target,"detected_tech":detected,"analysis":analysis})

@app.post("/intelligence/technology-detection")
def technology_detection():
    b = request.json or {}
    detected = tech_detect.detect(
        headers=b.get("headers",{}),
        body=b.get("body","")
    )
    return ok({"detected_technologies": detected})

@app.post("/intelligence/correlate-vulnerabilities")
def correlate_vulnerabilities():
    b    = request.json or {}
    vulns = b.get("vulnerabilities",[])
    return ok(vuln_corr.correlate(vulns))

# ── CVE Intelligence ──────────────────────────────────────────────────────────
@app.get("/cve/lookup/<technology>")
def cve_lookup(technology):
    version = request.args.get("version")
    return ok(cve_intel.lookup(technology, version))

@app.get("/cve/enrich/<cve_id>")
def cve_enrich(cve_id):
    return ok(cve_intel.enrich(cve_id))

# ── Exploit generation ────────────────────────────────────────────────────────
@app.post("/exploit/generate")
def exploit_generate():
    b = request.json or {}
    vuln_type = b.get("vuln_type","")
    if not vuln_type:
        return err("'vuln_type' is required")
    result = exploit_gen.generate(vuln_type, b.get("target","TARGET"), **b.get("params",{}))
    return ok(result)

@app.get("/exploit/templates")
def exploit_templates():
    return ok({"templates": list(exploit_gen.TEMPLATES.keys())})

# ── Bug Bounty ────────────────────────────────────────────────────────────────
@app.post("/bugbounty/start")
def bugbounty_start():
    b      = request.json or {}
    target = b.get("target","")
    if not target:
        return err("'target' is required")
    return ok(bb_manager.start_workflow(target, b.get("scope",[])))

@app.post("/bugbounty/phase-commands")
def bugbounty_phase_commands():
    b     = request.json or {}
    cmds  = bb_manager.get_phase_commands(b.get("target",""), b.get("phase","subdomain_discovery"))
    return ok({"commands": cmds})

@app.post("/bugbounty/full-recon")
def bugbounty_full_recon():
    b      = request.json or {}
    target = b.get("target","")
    if not target:
        return err("'target' is required")
    return ok(bb_agent.full_recon(target, b.get("scope",[])))

@app.get("/bugbounty/vuln-priorities")
def bugbounty_vuln_priorities():
    return ok({"priorities": bb_manager.VULN_PRIORITY})

# ── CTF ───────────────────────────────────────────────────────────────────────
@app.post("/ctf/solve")
def ctf_solve():
    b = request.json or {}
    return ok(ctf_manager.solve(b.get("category","web"), b.get("name","unknown"), b.get("hints",[])))

@app.post("/ctf/full-solve")
def ctf_full_solve():
    b = request.json or {}
    return ok(ctf_agent.solve_challenge(b.get("category","web"), b.get("name","unknown"), b.get("hints",[])))

@app.get("/ctf/categories")
def ctf_categories():
    return ok({"categories": list(ctf_manager.CATEGORIES.keys())})

# ── Browser agent ─────────────────────────────────────────────────────────────
@app.post("/browser/navigate")
def browser_navigate():
    b   = request.json or {}
    url = b.get("url","")
    if not url:
        return err("'url' is required")
    return ok(browser.navigate(url))

@app.post("/browser/screenshot")
def browser_screenshot():
    b = request.json or {}
    return ok(browser.screenshot(b.get("url")))

@app.post("/browser/extract-dom")
def browser_dom():
    b   = request.json or {}
    url = b.get("url")
    if url:
        browser.navigate(url)
    return ok(browser.extract_dom())

@app.post("/browser/cookies")
def browser_cookies():
    b = request.json or {}
    if b.get("url"):
        browser.navigate(b["url"])
    return ok({"cookies": browser.get_cookies()})

@app.post("/browser/security-headers")
def browser_security_headers():
    b   = request.json or {}
    url = b.get("url","")
    if not url:
        return err("'url' is required")
    return ok(browser.detect_missing_headers(url))

@app.post("/browser/full-analysis")
def browser_full_analysis():
    b   = request.json or {}
    url = b.get("url","")
    if not url:
        return err("'url' is required")
    return ok(browser.full_analysis(url))

# ── Tool-specific endpoints (major tools) ─────────────────────────────────────
TOOL_COMMANDS = {
    "nmap":           "nmap {flags} {target}",
    "masscan":        "masscan {target} {flags}",
    "rustscan":       "rustscan -a {target} {flags}",
    "nikto":          "nikto -h {target} {flags}",
    "sqlmap":         "sqlmap -u {target} {flags} --batch",
    "ffuf":           "ffuf -u {target}/FUZZ -w /usr/share/wordlists/dirb/common.txt {flags}",
    "nuclei":         "nuclei -u {target} {flags}",
    "subfinder":      "subfinder -d {target} {flags}",
    "amass":          "amass enum -d {target} {flags}",
    "httpx":          "httpx -u {target} {flags}",
    "katana":         "katana -u {target} {flags}",
    "gau":            "gau {target}",
    "waybackurls":    "waybackurls {target}",
    "dirsearch":      "dirsearch -u {target} {flags}",
    "paramspider":    "paramspider -d {target} {flags}",
    "arjun":          "arjun -u {target} {flags}",
    "x8":             "x8 -u {target} {flags}",
    "hydra":          "hydra -l {user} -P {wordlist} {target} {service}",
    "medusa":         "medusa -h {target} -u {user} -P {wordlist} -M {service}",
    "hashcat":        "hashcat -m {mode} {hash_file} {wordlist} {flags}",
    "john":           "john {hash_file} --wordlist={wordlist} {flags}",
    "wpscan":         "wpscan --url {target} {flags}",
    "enum4linux":     "enum4linux -a {target}",
    "smbmap":         "smbmap -H {target} {flags}",
    "crackmapexec":   "crackmapexec smb {target} {flags}",
    "metasploit":     "msfconsole -q -x '{flags}'",
    "searchsploit":   "searchsploit {query}",
    "checksec":       "checksec --file={target}",
    "binwalk":        "binwalk {target} {flags}",
    "strings":        "strings {target} {flags}",
    "ropgadget":      "ROPgadget --binary {target} {flags}",
    "volatility":     "volatility -f {target} {flags}",
    "wireshark":      "tshark -r {target} {flags}",
    "exiftool":       "exiftool {target}",
    "steghide":       "steghide {flags} {target}",
    "zsteg":          "zsteg {target} {flags}",
    "theHarvester":   "theHarvester -d {target} -b all",
    "shodan":         "shodan host {target}",
    "whois":          "whois {target}",
    "dig":            "dig {target} {flags}",
    "dnsx":           "dnsx -d {target} {flags}",
    "assetfinder":    "assetfinder --subs-only {target}",
    "commix":         "commix --url={target} {flags}",
    "xsser":          "xsser -u {target} {flags}",
    "wfuzz":          "wfuzz -u {target}/FUZZ -w /usr/share/wordlists/dirb/common.txt {flags}",
    "gobuster":       "gobuster dir -u {target} -w /usr/share/wordlists/dirb/common.txt {flags}",
    "feroxbuster":    "feroxbuster -u {target} {flags}",
    "curl":           "curl -s {flags} {target}",
    "wget":           "wget {flags} {target}",
    "openssl":        "openssl {flags} {target}",
    "netcat":         "nc {flags} {target}",
    "tcpdump":        "tcpdump {flags}",
    "arp-scan":       "arp-scan {flags} {target}",
    "dnsenum":        "dnsenum {target} {flags}",
    "fierce":         "fierce --domain {target} {flags}",
    "recon-ng":       "recon-ng {flags}",
    "maltego":        "maltego {flags}",
}

def _build_tool_route(tool_name):
    def route():
        b       = request.json or {}
        target  = b.get("target","")
        flags   = b.get("flags","")
        tmpl    = TOOL_COMMANDS.get(tool_name,"echo 'tool not configured'")
        cmd     = tmpl.format(target=target, flags=flags,
                              query=b.get("query",target),
                              user=b.get("user","admin"),
                              wordlist=b.get("wordlist","/usr/share/wordlists/rockyou.txt"),
                              service=b.get("service","ssh"),
                              mode=b.get("mode","0"),
                              hash_file=b.get("hash_file","hashes.txt"))
        logger.info("🔧 Tool [%s]: %s", tool_name, cmd)
        result  = run_cmd(cmd, b.get("timeout", 120))
        return ok({"tool": tool_name, **result})
    route.__name__ = f"tool_{tool_name.replace('-','_')}"
    return route

for _tool in TOOL_COMMANDS:
    safe = _tool.replace("-","_").lower()
    app.add_url_rule(f"/tools/{_tool}", view_func=_build_tool_route(_tool), methods=["POST"])

@app.get("/tools")
def list_tools():
    return ok({"tools": list(TOOL_COMMANDS.keys()), "count": len(TOOL_COMMANDS)})

# ── File operations ───────────────────────────────────────────────────────────
@app.post("/files/write")
def file_write():
    b    = request.json or {}
    name = b.get("filename","")
    if not name:
        return err("'filename' is required")
    path = FILE_DIR / Path(name).name
    content = b.get("content","")
    total_size = sum(f.stat().st_size for f in FILE_DIR.rglob("*") if f.is_file())
    if total_size + len(content) > MAX_FILE_MB * 1024 * 1024:
        return err("Storage quota exceeded (100MB)", 413)
    path.write_text(content, encoding="utf-8")
    return ok({"path": str(path), "size": len(content)})

@app.get("/files/read/<filename>")
def file_read(filename):
    path = FILE_DIR / Path(filename).name
    if not path.exists():
        return err(f"{filename} not found", 404)
    return ok({"filename": filename, "content": path.read_text(encoding="utf-8")})

@app.get("/files/list")
def file_list():
    files = [{"name": e.name, "size": (st := e.stat()).st_size, "modified": st.st_mtime}
             for e in os.scandir(FILE_DIR) if e.is_file()]
    return ok({"files": files, "count": len(files)})

@app.delete("/files/<filename>")
def file_delete(filename):
    path = FILE_DIR / Path(filename).name
    if not path.exists():
        return err(f"{filename} not found", 404)
    path.unlink()
    return ok({"deleted": filename})

# ── Visual / rendering ────────────────────────────────────────────────────────
@app.post("/visual/progress")
def visual_progress():
    b = request.json or {}
    bar = progress_bar(b.get("percent", 50), b.get("width", 40), b.get("label",""))
    return ok({"progress_bar": bar})

@app.post("/visual/severity-card")
def visual_severity_card():
    b = request.json or {}
    card = severity_card(b.get("title","Finding"), b.get("severity","info"), b.get("detail",""))
    return ok({"card": card})

@app.post("/visual/table")
def visual_table():
    b = request.json or {}
    table = tabular(b.get("headers",[]), b.get("rows",[]))
    return ok({"table": table})

# ── Cache & telemetry ─────────────────────────────────────────────────────────
@app.get("/cache/stats")
def cache_stats():
    return ok(cache.stats())

@app.post("/cache/invalidate")
def cache_invalidate():
    b   = request.json or {}
    key = b.get("key")
    if key:
        cache.delete(key)
        return ok({"invalidated": key})
    cache.clear()
    return ok({"invalidated": "all"})

@app.get("/telemetry/performance")
def telemetry_performance():
    return ok(perf_mon.summary())

@app.get("/telemetry/errors")
def telemetry_errors():
    n = int(request.args.get("n", 50))
    return ok({"errors": err_hist.recent(n)})

@app.get("/telemetry/failures")
def telemetry_failures():
    return ok({"failures": fail_rec.stats()})

@app.get("/telemetry/rate-limits")
def telemetry_rate_limits():
    return ok({"info": "Rate limit tracking active", "windows": rate_detect._windows})

# ── Error history ─────────────────────────────────────────────────────────────
@app.get("/errors")
def errors():
    return ok({"errors": err_hist.recent(100)})

@app.delete("/errors")
def errors_clear():
    err_hist.clear()
    return ok({"cleared": True})

# ── System info ───────────────────────────────────────────────────────────────
@app.get("/system/info")
def system_info():
    try:
        import psutil
        info = {
            "cpu_percent":    psutil.cpu_percent(interval=0.5),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent":   psutil.disk_usage("/").percent,
            "platform":       sys.platform,
        }
    except Exception:
        info = {"platform": sys.platform}
    return ok(info)

# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print_banner()
    logger.info("%s🚀 Majestic AI v1.0 starting on 0.0.0.0:%d%s", HACKER_RED, args.port, RESET)
    app.run(host="0.0.0.0", port=args.port, debug=args.debug, threaded=True)
