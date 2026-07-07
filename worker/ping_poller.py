import re, subprocess
from dataclasses import dataclass

@dataclass
class PingResult:
    success: bool
    latency_ms: float | None = None
    error_message: str | None = None

def ping(host: str, timeout_seconds: int = 3) -> PingResult:
    try:
        proc = subprocess.run(["ping", "-c", "1", "-W", str(timeout_seconds), host], capture_output=True, text=True, timeout=timeout_seconds + 2)
        output = (proc.stdout or "") + (proc.stderr or "")
        if proc.returncode == 0:
            match = re.search(r"time[=<]([0-9.]+)\s*ms", output)
            return PingResult(True, float(match.group(1)) if match else None)
        return PingResult(False, None, output.strip() or "Ping failed")
    except Exception as exc:
        return PingResult(False, None, str(exc))
