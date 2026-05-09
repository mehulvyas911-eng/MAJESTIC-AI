import time
from pathlib import Path

FILE_DIR = Path("/tmp/hexstrike_files")
FILE_DIR.mkdir(parents=True, exist_ok=True)

# Create 10,000 files
for i in range(10000):
    (FILE_DIR / f"file_{i}.txt").touch()

def benchmark_old():
    t0 = time.time()
    files = [{"name":f.name,"size":f.stat().st_size,"modified":f.stat().st_mtime}
             for f in FILE_DIR.iterdir() if f.is_file()]
    t1 = time.time()
    return t1 - t0

def benchmark_new():
    t0 = time.time()
    files = [{"name": f.name, "size": (st := f.stat()).st_size, "modified": st.st_mtime}
             for f in FILE_DIR.iterdir() if f.is_file()]
    t1 = time.time()
    return t1 - t0

def benchmark_scandir():
    import os
    t0 = time.time()
    files = []
    for entry in os.scandir(FILE_DIR):
        if entry.is_file():
            st = entry.stat()
            files.append({"name": entry.name, "size": st.st_size, "modified": st.st_mtime})
    t1 = time.time()
    return t1 - t0

print("Old:", benchmark_old())
print("New (walrus):", benchmark_new())
print("New (scandir):", benchmark_scandir())
