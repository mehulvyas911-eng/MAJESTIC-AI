import time
import os
from pathlib import Path

FILE_DIR = Path("/tmp/hexstrike_files")
FILE_DIR.mkdir(parents=True, exist_ok=True)

for i in range(10000):
    (FILE_DIR / f"file_{i}.txt").touch()

def benchmark_scandir_list_comp():
    t0 = time.time()
    files = [{"name": e.name, "size": (st := e.stat()).st_size, "modified": st.st_mtime}
             for e in os.scandir(FILE_DIR) if e.is_file()]
    t1 = time.time()
    return t1 - t0

print("New (scandir list comp):", benchmark_scandir_list_comp())
