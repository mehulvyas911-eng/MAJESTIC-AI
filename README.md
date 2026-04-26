# Majestic AI v1.0 🔴
### AI-Powered Cybersecurity Automation Platform

```
╔══════════════════════════════════════════════════════╗
║   MAJESTIC AI  v1.0  |  MCP Platform  |  Port 8888  ║
╚══════════════════════════════════════════════════════╝
```

---

## Architecture

```
AI Agent (Claude/GPT/Copilot)
        │  MCP Protocol
        ▼
  mcp_client.py          ← FastMCP wrapper (50+ tool definitions)
        │  HTTP/REST
        ▼
   server.py             ← Flask API (0.0.0.0:8888)
        │
        ├── agents.py         (12 AI agent classes)
        ├── cache_engine.py   (LRU cache + process registry)
        ├── error_engine.py   (10 error types + retry + degradation)
        ├── visual_engine.py  (blood-red ANSI terminal UI)
        └── browser_agent.py  (Selenium headless Chrome)
```

---

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the API server
```bash
# Default (port 8888)
python server.py

# Custom port
python server.py --port 9000

# Debug mode
python server.py --debug

# Via env var
set HEXSTRIKE_PORT=9000 && python server.py
```

### 3. Connect an AI agent via MCP
```bash
python mcp_client.py --server http://localhost:8888
```

### 4. Configure Claude Desktop
Copy `claude_mcp_config.json` contents into:
`%APPDATA%\Claude\claude_desktop_config.json`

---

## API Endpoints (50+)

| Category | Endpoints |
|---|---|
| Core | `GET /health`, `GET /`, `GET /banner` |
| Execution | `POST /execute`, `POST /execute/stream` |
| Processes | `GET /processes`, `POST /processes/{pid}/pause|resume|terminate` |
| Intelligence | `POST /intelligence/analyze-target`, `select-tools`, `optimize-parameters`, `create-attack-chain`, `smart-scan`, `technology-detection`, `correlate-vulnerabilities` |
| CVE | `GET /cve/lookup/{tech}`, `GET /cve/enrich/{cve_id}` |
| Exploit | `POST /exploit/generate`, `GET /exploit/templates` |
| Bug Bounty | `POST /bugbounty/start`, `phase-commands`, `full-recon` |
| CTF | `POST /ctf/solve`, `ctf/full-solve`, `GET /ctf/categories` |
| Browser | `POST /browser/navigate|screenshot|extract-dom|cookies|security-headers|full-analysis` |
| Tools | `POST /tools/{tool_name}` (55+ tools) |
| Files | `POST /files/write`, `GET /files/read/{name}`, `GET /files/list`, `DELETE /files/{name}` |
| Visual | `POST /visual/progress|severity-card|table` |
| Telemetry | `GET /cache/stats`, `GET /telemetry/performance|errors|failures` |
| System | `GET /system/info`, `GET /errors` |

---

## 12 AI Agent Classes

| # | Agent | Purpose |
|---|---|---|
| 1 | `IntelligentDecisionEngine` | Ranks tools, builds attack chains with success probabilities |
| 2 | `BugBountyAgent` | Orchestrates full recon workflows |
| 3 | `CTFAgent` | CTF category solver with tool flows |
| 4 | `CVEIntelligenceManager` | CVE lookup and enrichment |
| 5 | `AIExploitGenerator` | PoC templates (8 vuln types) |
| 6 | `VulnerabilityCorrelator` | Chains vulns, calculates risk score |
| 7 | `TechnologyDetector` | Fingerprints tech from headers/body |
| 8 | `RateLimitDetector` | Detects 429s and rate-limit headers |
| 9 | `FailureRecoverySystem` | Tracks failures, suggests fallbacks |
| 10 | `PerformanceMonitor` | Avg duration, success rate per tool |
| 11 | `ParameterOptimizer` | Stealth/aggressive parameter tuning |
| 12 | `GracefulDegradation` | nmap→masscan→rustscan fallback chains |

---

## Bug Bounty Phases

| Phase | Tools | Timeout |
|---|---|---|
| Subdomain Discovery | amass, subfinder, assetfinder | 300s |
| HTTP Probing | httpx, nuclei | 180s |
| Content Discovery | katana, gau, waybackurls, dirsearch | 600s |
| Parameter Discovery | paramspider, arjun, x8 | 240s |

**Vulnerability Priority:** RCE(10) → SQLi(9) → SSRF/IDOR(8) → XSS/LFI(7) → XXE(6) → CSRF(5)

---

## CTF Categories

`web` | `crypto` | `pwn` | `forensics` | `reversing` | `misc` | `osint` | `stego`

**PWN flow:** `checksec → gdb-peda → ropgadget → pwntools`

---

## Error Handling

10 error types with exponential backoff (immediate → 5s → 10s, 3 retries):
`TIMEOUT` | `PERMISSION_DENIED` | `NETWORK_UNREACHABLE` | `RATE_LIMITED` | `TOOL_NOT_FOUND` | `INVALID_PARAMETERS` | `RESOURCE_EXHAUSTED` | `AUTHENTICATION_FAILED` | `TARGET_UNREACHABLE` | `PARSING_ERROR`

---

## Files

| File | Description |
|---|---|
| `server.py` | Flask REST API, 50+ endpoints, 0.0.0.0:8888 |
| `mcp_client.py` | FastMCP wrapper for AI agents |
| `agents.py` | 12 AI agent classes |
| `cache_engine.py` | LRU cache (1000 entries, 3600s TTL) |
| `error_engine.py` | Error taxonomy + retry + degradation |
| `visual_engine.py` | Blood-red ANSI terminal engine |
| `browser_agent.py` | Selenium headless Chrome agent |
| `claude_mcp_config.json` | Claude Desktop MCP config (300s timeout) |
| `requirements.txt` | Python dependencies |

---

> ⚠️ **Legal Notice:** For authorized security testing, bug bounty programs, and CTF competitions only.
