import requests
import json
import time

def run():
    # Test valid command
    data_valid = {"command": "echo hello"}
    r1 = requests.post("http://localhost:8889/execute", json=data_valid)
    print("Valid sync:", r1.json())

    r2 = requests.post("http://localhost:8889/execute/stream", json=data_valid)
    print("Valid stream:", r2.json())

    # Wait a bit for server to process
    time.sleep(1)

    # Test injection command
    data_injection = {"command": "echo 'hello'; touch /tmp/pwned2"}
    r3 = requests.post("http://localhost:8889/execute", json=data_injection)
    print("Inject sync:", r3.json())

    r4 = requests.post("http://localhost:8889/execute/stream", json=data_injection)
    print("Inject stream:", r4.json())

if __name__ == "__main__":
    run()
