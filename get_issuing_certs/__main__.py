import sys
from get_issuing_certs import (
    check_ca_true,
    get_certificates,
    is_cert_in_file,
    parse_args,
)


def main() -> None:
    """main script bits"""
    config = parse_args()

    print(
        f"Checking {config['hostname']}:{config['port']} and adding to {config['filename']}",
        file=sys.stderr,
    )

    certificates = get_certificates(config["hostname"], config["port"])

    if len(certificates) <= 1:
        print("No issuing certificates found.", file=sys.stderr)
        sys.exit(1)

    for idx, cert in enumerate(certificates):
        if not check_ca_true(cert):
            continue
        if not is_cert_in_file(cert, config["filename"]):
            print(f"Certificate {idx} not found in file, adding it!", file=sys.stderr)
            with open(config["filename"], "a") as f:
                f.write(f"\n{cert}\n")
        else:
            print(f"Certificate {idx} already in file", file=sys.stderr)

    # clean up the file
    with open(config["filename"], "r") as f:
        lines = f.readlines()
    # strip blank lines
    lines = [line.strip() for line in lines if line.strip()]

    # write it back, with a trailing newline
    with open(config["filename"], "w") as f:
        f.write("\n".join(lines))
        f.write("\n")


if __name__ == "__main__":
    main()
