#!/usr/bin/env python

# simple script to compute a key from public and private components

import base64
from pathlib import Path


# read key files, decode the public integer, and divide by the private divisor
def main():
    try:
        pub_text = Path("pub.key").read_text(encoding="utf-8").strip()
        decoded_bytes = base64.b64decode(pub_text)
        num = int(decoded_bytes.decode("utf-8"))

        priv_text = Path("private.key").read_text(encoding="utf-8").strip()
        divisor = int(priv_text)

        key = num / divisor
        print(f"key: {key}")

    except FileNotFoundError as err:
        print(f"Error: Missing required key file - {err.filename}")
    except (ValueError, base64.binascii.Error) as err:
        print(f"Error: Invalid key format or data - {err}")
    except ZeroDivisionError:
        print("Error: Private key cannot be zero.")


if __name__ == "__main__":
    main()