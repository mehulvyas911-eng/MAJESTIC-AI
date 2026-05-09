"""
Majestic AI v1.0 - Terminal Visual Engine
Blood-red ANSI palette, ASCII art banner, progress bars, severity cards
"""
import io, sys
# Force UTF-8 output on Windows so ANSI/Unicode prints correctly
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
import time
import threading

def ansi(code): return f"\033[{code}m"
def fg256(n):   return f"\033[38;5;{n}m"
def bg256(n):   return f"\033[48;5;{n}m"
RESET   = "\033[0m"
BOLD    = "\033[1m"

# ── Colour palette ──────────────────────────────────────────────────────────
CRIMSON   = fg256(160)
BLOOD_RED = fg256(124)
HACKER_RED= fg256(196)
GREEN     = fg256(46)
ORANGE    = fg256(208)
CYAN      = fg256(51)
GRAY      = fg256(240)
WHITE     = "\033[97m"
YELLOW    = fg256(226)

# Severity bg colours
BG_DARK_RED = bg256(52)
BG_BLACK    = bg256(232)

SEV_CRITICAL= f"{BG_DARK_RED}{BOLD}{WHITE}"
SEV_HIGH    = f"{HACKER_RED}{BOLD}"
SEV_MEDIUM  = f"{ORANGE}{BOLD}"
SEV_LOW     = YELLOW
SEV_INFO    = CYAN

BANNER = (
    f"{BLOOD_RED}{BOLD}\n"
    f"+======================================================================+\n"
    f"|  {HACKER_RED}MAJESTIC AI  v1.0{BLOOD_RED}                                                  |\n"
    f"|  {CRIMSON}AI-Powered Cybersecurity Automation Platform | MCP Edition{BLOOD_RED}         |\n"
    f"|  {GRAY}Port 8888  |  150+ Tools  |  12 AI Agents  |  50+ API Endpoints{BLOOD_RED}    |\n"
    f"+======================================================================+{RESET}\n"
)

def print_banner():
    print(BANNER)

def progress_bar(pct: float, width: int = 40, label: str = "") -> str:
    """Return a stylised ASCII progress bar."""
    pct = max(0.0, min(1.0, pct))
    filled = int(width * pct)
    empty  = width - filled
    bar    = (bg256(196) + " " * filled + RESET +
              bg256(236) + " " * empty + RESET)
    return f"[{bar}] {BOLD}{pct*100:5.1f}%{RESET} {GRAY}{label}{RESET}"

BRAILLE_FRAMES = ["||","/|","//","|/","||","\\\\","\\\\","|\\\\"]

class Spinner:
    def __init__(self, msg: str = "Working"):
        self.msg   = msg
        self._stop = threading.Event()
        self._t    = threading.Thread(target=self._spin, daemon=True)

    def __enter__(self):
        self._t.start(); return self

    def __exit__(self, *_):
        self._stop.set(); self._t.join()
        sys.stdout.write(f"\r{' ' * (len(self.msg)+6)}\r"); sys.stdout.flush()

    def _spin(self):
        i = 0
        while not self._stop.is_set():
            f = BRAILLE_FRAMES[i % len(BRAILLE_FRAMES)]
            sys.stdout.write(f"\r{HACKER_RED}{f}{RESET} {CYAN}{self.msg}...{RESET}")
            sys.stdout.flush()
            time.sleep(0.1); i += 1

def severity_card(title: str, severity: str, detail: str) -> str:
    sev = severity.upper()
    colour_map = {
        "CRITICAL": SEV_CRITICAL,
        "HIGH":     SEV_HIGH,
        "MEDIUM":   SEV_MEDIUM,
        "LOW":      SEV_LOW,
        "INFO":     SEV_INFO,
    }
    c = colour_map.get(sev, SEV_INFO)
    box = (
        f"{BLOOD_RED}┌─ {c}[{sev}]{RESET} {BOLD}{title}{RESET}\n"
        f"{BLOOD_RED}│  {GRAY}{detail}{RESET}\n"
        f"{BLOOD_RED}└{'─'*60}{RESET}"
    )
    return box

def tabular(headers: list, rows: list) -> str:
    widths = [max(len(str(h)), max((len(str(r[i])) for r in rows), default=0))
              for i, h in enumerate(headers)]
    sep  = BLOOD_RED + "├" + "┼".join("─"*(w+2) for w in widths) + "┤" + RESET
    top  = BLOOD_RED + "┌" + "┬".join("─"*(w+2) for w in widths) + "┐" + RESET
    bot  = BLOOD_RED + "└" + "┴".join("─"*(w+2) for w in widths) + "┘" + RESET

    def row_line(cells, colour=GRAY):
        parts = [f" {colour}{str(c).ljust(w)}{RESET} " for c, w in zip(cells, widths)]
        return BLOOD_RED + "│" + "│".join(parts) + "│" + RESET

    lines = [top, row_line(headers, CYAN + BOLD), sep]
    for r in rows:
        lines.append(row_line(r))
    lines.append(bot)
    return "\n".join(lines)
