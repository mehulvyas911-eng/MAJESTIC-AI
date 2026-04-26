"""
Majestic AI v1.0 – Headless Browser Agent
Selenium + ChromeDriver: navigate, screenshot, DOM extraction, cookies, security headers.
"""
import logging
import base64
from typing import Optional

logger = logging.getLogger("majestic.browser")

SECURITY_HEADERS = [
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Strict-Transport-Security",
    "X-XSS-Protection",
    "Referrer-Policy",
    "Permissions-Policy",
    "Cross-Origin-Opener-Policy",
    "Cross-Origin-Embedder-Policy",
    "Cross-Origin-Resource-Policy",
]

class HeadlessBrowserAgent:
    def __init__(self):
        self._driver = None

    def _init_driver(self):
        if self._driver:
            return
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager

            opts = Options()
            opts.add_argument("--headless=new")
            opts.add_argument("--no-sandbox")
            opts.add_argument("--disable-dev-shm-usage")
            opts.add_argument("--disable-gpu")
            opts.add_argument("--window-size=1920,1080")
            opts.add_argument("--ignore-certificate-errors")

            service = Service(ChromeDriverManager().install())
            self._driver = webdriver.Chrome(service=service, options=opts)
            logger.info("🌐 ChromeDriver initialised")
        except Exception as e:
            logger.error("ChromeDriver init failed: %s", e)
            raise RuntimeError(f"ChromeDriver unavailable: {e}")

    def navigate(self, url: str) -> dict:
        self._init_driver()
        try:
            self._driver.get(url)
            return {"url": url, "title": self._driver.title,
                    "current_url": self._driver.current_url, "status": "ok"}
        except Exception as e:
            return {"url": url, "error": str(e), "status": "failed"}

    def screenshot(self, url: str = None) -> dict:
        self._init_driver()
        if url:
            self._driver.get(url)
        try:
            png_b64 = self._driver.get_screenshot_as_base64()
            return {"screenshot_b64": png_b64, "format": "png",
                    "url": self._driver.current_url}
        except Exception as e:
            return {"error": str(e)}

    def extract_dom(self) -> dict:
        from selenium.webdriver.common.by import By
        try:
            links  = [a.get_attribute("href") for a in
                      self._driver.find_elements(By.TAG_NAME, "a") if a.get_attribute("href")]
            forms  = []
            for f in self._driver.find_elements(By.TAG_NAME, "form"):
                forms.append({
                    "action": f.get_attribute("action"),
                    "method": f.get_attribute("method"),
                    "inputs": [{"name": i.get_attribute("name"),
                                "type": i.get_attribute("type")}
                               for i in f.find_elements(By.TAG_NAME, "input")],
                })
            scripts = [s.get_attribute("src") or s.get_attribute("innerHTML")[:80]
                       for s in self._driver.find_elements(By.TAG_NAME, "script")]
            return {"links": links[:100], "forms": forms[:20], "scripts": scripts[:30],
                    "url": self._driver.current_url}
        except Exception as e:
            return {"error": str(e)}

    def get_cookies(self) -> list:
        try:
            return self._driver.get_cookies()
        except Exception as e:
            return [{"error": str(e)}]

    def detect_missing_headers(self, url: str) -> dict:
        import requests
        try:
            r = requests.get(url, timeout=15, verify=False)
            present = {h: r.headers.get(h) for h in SECURITY_HEADERS if h in r.headers}
            missing = [h for h in SECURITY_HEADERS if h not in r.headers]
            return {
                "url":             url,
                "present_headers": present,
                "missing_headers": missing,
                "risk_level":      "HIGH" if len(missing) > 5 else
                                   "MEDIUM" if len(missing) > 2 else "LOW",
            }
        except Exception as e:
            return {"url": url, "error": str(e)}

    def full_analysis(self, url: str) -> dict:
        nav    = self.navigate(url)
        dom    = self.extract_dom()
        shot   = self.screenshot()
        cook   = self.get_cookies()
        hdrs   = self.detect_missing_headers(url)
        return {
            "navigation":       nav,
            "dom":              dom,
            "cookies":          cook,
            "security_headers": hdrs,
            "screenshot_b64":   shot.get("screenshot_b64"),
        }

    def close(self):
        if self._driver:
            try:
                self._driver.quit()
            except Exception:
                pass
            self._driver = None
