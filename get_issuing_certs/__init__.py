import argparse
from pathlib import Path
import subprocess
import shutil
import re
from typing import Any, Dict, List, Optional


def get_certificates(hostname: str, port: str) -> List[Any]:
    cmd = [
        "openssl",
        "s_client",
        "-connect",
        f"{hostname}:{port}",
        "-showcerts",
        "-servername",
        hostname,
    ]
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE
    )
    out, _ = proc.communicate(input=b"HEAD / HTTP/1.0\n\n")
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


def parse_args() -> Dict[str, str]:
    """parse argv and do the thing"""
    parser = argparse.ArgumentParser(
        description="A script to do something with a hostname, port, and filename."
    )

    # Required argument
    parser.add_argument("hostname", type=str, help="The hostname to connect to.")

    # Optional arguments with default values
    parser.add_argument(
        "--port",
        type=str,
        default="443",
        help="The port to connect to. Default is 443.",
    )
    parser.add_argument(
        "--filename",
        type=str,
        default="output.txt",
        help="The name of the output file. Default is output.txt.",
    )
    args = parser.parse_args()

    return {
        "filename": args.filename,
        "hostname": args.hostname,
        "port": args.port,
    }
