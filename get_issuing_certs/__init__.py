from pathlib import Path
import subprocess
import shutil
import sys
import re
from typing import Any, Dict, List, Optional


def get_certificates(hostname: str, port: str) -> List[Any]:
    cmd = ["openssl", "s_client", "-connect", f"{hostname}:{port}", "-showcerts"]
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE
    )
    out, _ = proc.communicate(input=b"")
    cert_data = out.decode()

    return re.findall(
        r"-----BEGIN CERTIFICATE-----.+?-----END CERTIFICATE-----", cert_data, re.DOTALL
    )


def find_openssl_in_path() -> Optional[str]:
    """tries to find openssl in the path"""
    return shutil.which("openssl")


def save_certificates(certificates: List[str]) -> int:
    saved = 0
    for i, cert in enumerate(certificates):
        if check_ca_true(cert):
            with open(f"cert_{i}.pem", "w") as f:
                f.write(cert)
            saved += 1
    return saved


def check_ca_true(cert_string: str) -> bool:
    cmd = ["openssl", "x509", "-text", "-noout"]
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE
    )
    out, _ = proc.communicate(input=cert_string.encode())
    return "CA:TRUE" in out.decode()


def is_cert_in_file(cert_string: str, file_path: str) -> bool:
    try:
        file_contents = Path(file_path).read_text(encoding="utf-8")
        # Normalize the string (remove leading/trailing whitespaces) for accurate comparison
        cert_string = cert_string.strip()

        return cert_string in file_contents

    except FileNotFoundError:
        print(f"The file {file_path} was not found.")
        return False


def parse_argv() -> Dict[str, str]:
    """parse argv and do the thing"""
    if len(sys.argv) < 2:
        print(f"Usage: {__file__} hostname <port>", file=sys.stderr)
        sys.exit(1)

    if find_openssl_in_path() is None:
        print("Can't find openssl in the shell!", file=sys.stderr)
        sys.exit(1)

    hostname = sys.argv[1]
    if len(sys.argv) > 2:
        port = sys.argv[2]
    else:
        port = "443"

    if len(sys.argv) >= 3:
        target_file = sys.argv[2]
    else:
        target_file = "/opt/splunkforwarder/etc/auth/appsCA.pem"
    return {
        "target_file": target_file,
        "hostname": hostname,
        "port": port,
    }
