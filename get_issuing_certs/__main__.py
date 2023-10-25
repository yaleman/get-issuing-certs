import sys
from get_issuing_certs import (
    check_ca_true,
    get_certificates,
    is_cert_in_file,
    parse_argv,
)


def main() -> None:
    """main script bits"""
    config = parse_argv()

    print(
        f"Checking {config['hostname']}:{config['port']} and adding to {config['target_file']}",
        file=sys.stderr,
    )

    certificates = get_certificates(config["hostname"], config["port"])

    if len(certificates) <= 1:
        print("No issuing certificates found.", file=sys.stderr)
        sys.exit(1)

    for idx, cert in enumerate(certificates):
        if not check_ca_true(cert):
            continue
        if not is_cert_in_file(cert, config["target_file"]):
            print(f"Certificate {idx} not found in file, adding it!", file=sys.stderr)
            with open(config["target_file"], "a") as f:
                f.write(f"\n{cert}")
        else:
            print(f"Certificate {idx} already in file", file=sys.stderr)


if __name__ == "__main__":
    main()