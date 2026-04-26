"""
Majestic AI v1.0 – FastMCP Client Wrapper
Exposes all server capabilities as MCP tools for Claude, GPT, Copilot, etc.
Usage: python mcp_client.py [--server http://localhost:8888]
"""
import os, sys, json, argparse
import requests

# ── Resolve server URL ────────────────────────────────────────────────────────
parser = argparse.ArgumentParser()
parser.add_argument("--server", default=os.environ.get("MAJESTIC_SERVER","http://localhost:8888"))
args, _ = parser.parse_known_args()
SERVER  = args.server.rstrip("/")

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("ERROR: 'mcp' package not found. Run: pip install mcp", file=sys.stderr)
    sys.exit(1)

mcp = FastMCP("Majestic AI v1.0")

# ── Helper ────────────────────────────────────────────────────────────────────
def _post(endpoint: str, payload: dict) -> dict:
    try:
        r = requests.post(f"{SERVER}{endpoint}", json=payload, timeout=300)
        return r.json()
    except Exception as e:
        return {"status":"error","message":str(e)}

def _get(endpoint: str, params: dict = None) -> dict:
    try:
        r = requests.get(f"{SERVER}{endpoint}", params=params, timeout=60)
        return r.json()
    except Exception as e:
        return {"status":"error","message":str(e)}

# ═══════════════════════════════════════════════════════════════════════════════
# CORE TOOLS
# ═══════════════════════════════════════════════════════════════════════════════
@mcp.tool()
def health_check() -> dict:
    """Check Majestic AI server health and uptime."""
    return _get("/health")

@mcp.tool()
def execute_command(command: str, timeout: int = 60) -> dict:
    """Execute an arbitrary shell command on the server and return output.
    Results are cached for 5 minutes. Use timeout to cap long-running tasks."""
    return _post("/execute", {"command": command, "timeout": timeout})

@mcp.tool()
def execute_command_async(command: str) -> dict:
    """Start a command asynchronously. Returns a PID for tracking."""
    return _post("/execute/stream", {"command": command})

# ═══════════════════════════════════════════════════════════════════════════════
# PROCESS MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════
@mcp.tool()
def list_processes() -> dict:
    """List all registered background processes."""
    return _get("/processes")

@mcp.tool()
def process_status(pid: int) -> dict:
    """Get status of a specific process by PID."""
    return _get(f"/processes/{pid}")

@mcp.tool()
def pause_process(pid: int) -> dict:
    """Pause (suspend) a running process."""
    return _post(f"/processes/{pid}/pause", {})

@mcp.tool()
def resume_process(pid: int) -> dict:
    """Resume a paused process."""
    return _post(f"/processes/{pid}/resume", {})

@mcp.tool()
def terminate_process(pid: int) -> dict:
    """Terminate a process."""
    return _post(f"/processes/{pid}/terminate", {})

@mcp.tool()
def process_dashboard() -> dict:
    """View all processes including top system processes by CPU/memory."""
    return _get("/processes/dashboard")

# ═══════════════════════════════════════════════════════════════════════════════
# INTELLIGENCE ENGINE
# ═══════════════════════════════════════════════════════════════════════════════
@mcp.tool()
def analyze_target(target_type: str, technologies: list = None, objectives: list = None) -> dict:
    """Intelligent target analysis. target_type: web_app|network_host|api|cloud|binary.
    Returns ranked tools with effectiveness scores and multi-stage attack chains."""
    return _post("/intelligence/analyze-target", {
        "target_type":  target_type,
        "technologies": technologies or [],
        "objectives":   objectives or [],
    })

@mcp.tool()
def select_tools(target_type: str, technologies: list = None) -> dict:
    """Get ranked tool recommendations for a given target type."""
    return _post("/intelligence/select-tools", {
        "target_type": target_type, "technologies": technologies or []
    })

@mcp.tool()
def optimize_parameters(tool: str, context: dict = None) -> dict:
    """Get AI-optimized parameters for a security tool.
    Pass context={'stealth':True} or context={'aggressive':True}."""
    return _post("/intelligence/optimize-parameters", {"tool": tool, "context": context or {}})

@mcp.tool()
def create_attack_chain(target_type: str, technologies: list = None, objectives: list = None) -> dict:
    """Generate multi-stage attack chains with success probability calculations."""
    return _post("/intelligence/create-attack-chain", {
        "target_type": target_type,
        "technologies": technologies or [],
        "objectives": objectives or ["privilege_escalation","lateral_movement","data_exfiltration"],
    })

@mcp.tool()
def smart_scan(target: str, objectives: list = None) -> dict:
    """Auto-detect technologies and recommend tools for a target hostname/URL."""
    return _post("/intelligence/smart-scan", {"target": target, "objectives": objectives or []})

@mcp.tool()
def detect_technologies(headers: dict = None, body: str = "") -> dict:
    """Identify technologies from HTTP headers and/or response body."""
    return _post("/intelligence/technology-detection", {"headers": headers or {}, "body": body})

@mcp.tool()
def correlate_vulnerabilities(vulnerabilities: list) -> dict:
    """Correlate a list of vulnerabilities to find exploit chains and calculate risk score.
    Each vuln should be a dict with 'type' and 'severity' keys."""
    return _post("/intelligence/correlate-vulnerabilities", {"vulnerabilities": vulnerabilities})

# ═══════════════════════════════════════════════════════════════════════════════
# CVE INTELLIGENCE
# ═══════════════════════════════════════════════════════════════════════════════
@mcp.tool()
def cve_lookup(technology: str, version: str = None) -> dict:
    """Look up CVEs for a technology (e.g. 'apache', 'wordpress', 'log4j')."""
    params = {"version": version} if version else {}
    return _get(f"/cve/lookup/{technology}", params)

@mcp.tool()
def cve_enrich(cve_id: str) -> dict:
    """Get detailed info, exploits, and patches for a specific CVE ID."""
    return _get(f"/cve/enrich/{cve_id}")

# ═══════════════════════════════════════════════════════════════════════════════
# EXPLOIT GENERATION
# ═══════════════════════════════════════════════════════════════════════════════
@mcp.tool()
def generate_exploit(vuln_type: str, target: str = "TARGET", params: dict = None) -> dict:
    """Generate a PoC exploit template.
    vuln_type: buffer_overflow|web_rce|sqli|xss|lfi|xxe|auth_bypass|deserialization"""
    return _post("/exploit/generate", {"vuln_type": vuln_type, "target": target, "params": params or {}})

@mcp.tool()
def list_exploit_templates() -> dict:
    """List all available exploit template types."""
    return _get("/exploit/templates")

# ═══════════════════════════════════════════════════════════════════════════════
# BUG BOUNTY WORKFLOW
# ═══════════════════════════════════════════════════════════════════════════════
@mcp.tool()
def start_bug_bounty(target: str, scope: list = None) -> dict:
    """Start a 4-phase bug bounty recon workflow: subdomain discovery → HTTP probing
    → content discovery → parameter discovery."""
    return _post("/bugbounty/start", {"target": target, "scope": scope or []})

@mcp.tool()
def get_phase_commands(target: str, phase: str) -> dict:
    """Get ready-to-run commands for a specific bug bounty phase.
    phase: subdomain_discovery|http_probing|content_discovery|parameter_discovery"""
    return _post("/bugbounty/phase-commands", {"target": target, "phase": phase})

@mcp.tool()
def full_bug_bounty_recon(target: str, scope: list = None) -> dict:
    """Run complete bug bounty recon: tech detection + tool selection + workflow."""
    return _post("/bugbounty/full-recon", {"target": target, "scope": scope or []})

@mcp.tool()
def bug_bounty_vuln_priorities() -> dict:
    """Get vulnerability priority scores: RCE→SQLi→SSRF/IDOR→XSS/LFI→XXE→CSRF."""
    return _get("/bugbounty/vuln-priorities")

# ═══════════════════════════════════════════════════════════════════════════════
# CTF WORKFLOW
# ═══════════════════════════════════════════════════════════════════════════════
@mcp.tool()
def ctf_solve(category: str, name: str, hints: list = None) -> dict:
    """Get a CTF solving plan with tools and strategy.
    category: web|crypto|pwn|forensics|reversing|misc|osint|stego"""
    return _post("/ctf/solve", {"category": category, "name": name, "hints": hints or []})

@mcp.tool()
def ctf_full_solve(category: str, name: str, hints: list = None) -> dict:
    """Full CTF agent: solving plan + available exploit templates."""
    return _post("/ctf/full-solve", {"category": category, "name": name, "hints": hints or []})

@mcp.tool()
def ctf_categories() -> dict:
    """List all supported CTF categories."""
    return _get("/ctf/categories")

# ═══════════════════════════════════════════════════════════════════════════════
# BROWSER AGENT
# ═══════════════════════════════════════════════════════════════════════════════
@mcp.tool()
def browser_navigate(url: str) -> dict:
    """Navigate headless Chrome to a URL. Returns page title and final URL."""
    return _post("/browser/navigate", {"url": url})

@mcp.tool()
def browser_screenshot(url: str = None) -> dict:
    """Take a screenshot of the current or given URL. Returns base64 PNG."""
    return _post("/browser/screenshot", {"url": url})

@mcp.tool()
def browser_extract_dom(url: str = None) -> dict:
    """Extract links, forms, inputs, and scripts from the current page."""
    return _post("/browser/extract-dom", {"url": url})

@mcp.tool()
def browser_get_cookies(url: str = None) -> dict:
    """Read all cookies from the current browser session."""
    return _post("/browser/cookies", {"url": url})

@mcp.tool()
def browser_check_security_headers(url: str) -> dict:
    """Check which security headers are present or missing for a URL."""
    return _post("/browser/security-headers", {"url": url})

@mcp.tool()
def browser_full_analysis(url: str) -> dict:
    """Full browser analysis: navigation + DOM + cookies + security headers + screenshot."""
    return _post("/browser/full-analysis", {"url": url})

# ═══════════════════════════════════════════════════════════════════════════════
# SECURITY TOOLS (individual wrappers)
# ═══════════════════════════════════════════════════════════════════════════════
def _tool_fn(tool_name):
    def fn(target: str, flags: str = "", timeout: int = 120, **kwargs) -> dict:
        return _post(f"/tools/{tool_name}", {"target":target,"flags":flags,"timeout":timeout,**kwargs})
    fn.__name__ = tool_name.replace("-","_")
    fn.__doc__  = f"Run {tool_name} against a target. Provide target and optional flags."
    return fn

for _t in ["nmap","masscan","rustscan","nikto","sqlmap","ffuf","nuclei","subfinder",
           "amass","httpx","katana","gau","waybackurls","dirsearch","paramspider","arjun",
           "x8","hydra","hashcat","john","wpscan","enum4linux","smbmap","crackmapexec",
           "searchsploit","checksec","binwalk","strings","ropgadget","volatility",
           "exiftool","steghide","zsteg","theHarvester","whois","dig","dnsx",
           "assetfinder","commix","xsser","wfuzz","gobuster","feroxbuster",
           "curl","wget","openssl","netcat","tcpdump","medusa","wireshark"]:
    mcp.tool()(_tool_fn(_t))

# ═══════════════════════════════════════════════════════════════════════════════
# FILE OPERATIONS
# ═══════════════════════════════════════════════════════════════════════════════
@mcp.tool()
def write_file(filename: str, content: str) -> dict:
    """Write content to a file in /tmp/hexstrike_files (100MB quota)."""
    return _post("/files/write", {"filename": filename, "content": content})

@mcp.tool()
def read_file(filename: str) -> dict:
    """Read a file from /tmp/hexstrike_files."""
    return _get(f"/files/read/{filename}")

@mcp.tool()
def list_files() -> dict:
    """List all files in /tmp/hexstrike_files."""
    return _get("/files/list")

@mcp.tool()
def delete_file(filename: str) -> dict:
    """Delete a file from /tmp/hexstrike_files."""
    try:
        r = requests.delete(f"{SERVER}/files/{filename}", timeout=30)
        return r.json()
    except Exception as e:
        return {"status":"error","message":str(e)}

# ═══════════════════════════════════════════════════════════════════════════════
# TELEMETRY & CACHE
# ═══════════════════════════════════════════════════════════════════════════════
@mcp.tool()
def cache_stats() -> dict:
    """Get LRU cache statistics: entries, TTL, hit/miss info."""
    return _get("/cache/stats")

@mcp.tool()
def invalidate_cache(key: str = None) -> dict:
    """Invalidate a specific cache key, or all cache if key is omitted."""
    return _post("/cache/invalidate", {"key": key})

@mcp.tool()
def performance_metrics() -> dict:
    """Get tool performance metrics: avg duration, success rate per tool."""
    return _get("/telemetry/performance")

@mcp.tool()
def error_history(n: int = 50) -> dict:
    """Get recent error history (last n errors)."""
    return _get("/telemetry/errors", {"n": n})

@mcp.tool()
def system_info() -> dict:
    """Get server system info: CPU, memory, disk usage."""
    return _get("/system/info")

@mcp.tool()
def list_all_tools() -> dict:
    """List all 150+ security tools registered in the platform."""
    return _get("/tools")

# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print(f"🔴 Majestic AI v1.0 MCP Server starting → {SERVER}", file=sys.stderr)
    mcp.run(transport="stdio")
