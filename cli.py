#!/usr/bin/env python3
"""
Majestic AI v1.0 - Autonomous CLI Agent
Allows interacting with Majestic AI without Claude Desktop by acting as an autonomous LLM agent.
Requires OPENAI_API_KEY environment variable.
"""

import os
import sys
import json
import time
import argparse
import requests

from visual_engine import (
    print_banner, progress_bar, severity_card, tabular,
    Spinner, HACKER_RED, GREEN, CYAN, GRAY, RESET, BOLD
)

# ── Configuration ─────────────────────────────────────────────────────────────
SERVER = os.environ.get("MAJESTIC_SERVER", "http://localhost:8888")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print(f"{HACKER_RED}Error: OPENAI_API_KEY environment variable not set.{RESET}", file=sys.stderr)
    sys.exit(1)


SYSTEM_PROMPT = """You are Majestic AI, an autonomous AI-powered cybersecurity agent.
You have access to a local REST API that provides various cybersecurity tools and workflows.
You can call these tools using the `call_majestic_api` function.

API Endpoints Summary:
| Category | Endpoints |
|---|---|
| Core | GET /health |
| Execution | POST /execute (payload: {"command": "...", "timeout": 60}) |
| Processes | GET /processes, POST /processes/{pid}/pause|resume|terminate |
| Intelligence | POST /intelligence/analyze-target (payload: {"target_type": "...", "technologies": [], "objectives": []}) |
| Bug Bounty | POST /bugbounty/start (payload: {"target": "...", "scope": []}) |
| CTF | POST /ctf/solve (payload: {"category": "...", "name": "...", "hints": []}) |
| Tools | POST /tools/{tool_name} (payload: {"target": "...", "flags": "...", "timeout": 120}). Tools: nmap, masscan, sqlmap, nikto, ffuf, nuclei, etc. |
| Files | POST /files/write (payload: {"filename": "...", "content": "..."}), GET /files/read/{name}, GET /files/list, DELETE /files/{name} |

Execute your reasoning, call APIs as needed, and summarize findings for the user. Do not ask the user to perform actions that you can perform via the API.
"""

def call_majestic_api(method: str, endpoint: str, payload: dict = None) -> str:
    """Helper to call the local Majestic AI server."""
    url = f"{SERVER}{endpoint}"
    try:
        if method.upper() == "GET":
            r = requests.get(url, params=payload, timeout=120)
        else:
            r = requests.post(url, json=payload or {}, timeout=120)
        return r.text
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

class AutonomousAgent:
    def __init__(self):
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "call_majestic_api",
                    "description": "Call a Majestic AI REST API endpoint.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "method": {"type": "string", "enum": ["GET", "POST"]},
                            "endpoint": {"type": "string", "description": "The API endpoint path (e.g., /health, /tools/nmap)"},
                            "payload": {"type": "object", "description": "JSON payload/parameters for the request"}
                        },
                        "required": ["method", "endpoint"]
                    }
                }
            }
        ]

    def chat(self, user_input: str):
        self.messages.append({"role": "user", "content": user_input})

        while True:
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "gpt-4-turbo",  # or gpt-3.5-turbo, gpt-4o
                "messages": self.messages,
                "tools": self.tools,
                "tool_choice": "auto"
            }

            with Spinner("Thinking"):
                response = None
                try:
                    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
                    response.raise_for_status()
                    resp_json = response.json()
                except Exception as e:
                    print(f"\n{HACKER_RED}LLM Error: {e}{RESET}")
                    if response is not None and hasattr(response, "text"):
                        print(f"{GRAY}{response.text}{RESET}")
                    return

            message = resp_json["choices"][0]["message"]
            self.messages.append(message)

            if message.get("content"):
                print(f"\n{CYAN}Majestic AI:{RESET} {message['content']}")

            tool_calls = message.get("tool_calls")
            if not tool_calls:
                break

            for tool_call in tool_calls:
                fn_name = tool_call["function"]["name"]
                args_str = tool_call["function"]["arguments"]

                print(f"{GRAY}[*] Calling {fn_name}({args_str}){RESET}")

                try:
                    args = json.loads(args_str)
                    if fn_name == "call_majestic_api":
                        result = call_majestic_api(args["method"], args["endpoint"], args.get("payload"))
                    else:
                        result = json.dumps({"error": f"Unknown tool: {fn_name}"})
                except Exception as e:
                    result = json.dumps({"error": str(e)})

                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "name": fn_name,
                    "content": result
                })

def main():
    parser = argparse.ArgumentParser(description="Majestic AI Autonomous CLI")
    parser.add_argument("prompt", nargs="*", help="Initial task or prompt")
    args = parser.parse_args()

    print_banner()
    agent = AutonomousAgent()

    initial_prompt = " ".join(args.prompt)
    if initial_prompt:
        print(f"{BOLD}User:{RESET} {initial_prompt}")
        agent.chat(initial_prompt)

    while True:
        try:
            user_input = input(f"\n{BOLD}User >{RESET} ")
            if user_input.strip().lower() in ["exit", "quit"]:
                break
            if user_input.strip():
                agent.chat(user_input)
        except (KeyboardInterrupt, EOFError):
            print()
            break

if __name__ == "__main__":
    main()
