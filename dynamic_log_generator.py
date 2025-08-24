
import time
import random

templates = [
    "[INFO] CPU usage high",
    "[WARN] Memory usage at {}%",
    "[ERROR] Request failed with status {}",
    "[CRITICAL] Disk space low on {}",
    "[INFO] Service {} restarted successfully"
]

params = [
    lambda: random.randint(70, 100),
    lambda: random.choice(["200", "400", "500"]),
    lambda: random.choice(["/dev/sda1", "/dev/sdb2"]),
    lambda: random.choice(["auth-service", "payment-service", "db-service"])
]

log_file = "dynamic_logs.txt"

with open(log_file, "a") as f:
    while True:
        template = random.choice(templates)
        if "{}" in template:
            param = random.choice(params)()
            log_line = template.format(param)
        else:
            log_line = template
        f.write(log_line + "\n")
        f.flush()
        print(f"[Generated] {log_line}")
        time.sleep(1)
