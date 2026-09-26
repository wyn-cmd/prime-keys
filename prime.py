#!/usr/bin/env python
import base64
from pathlib import Path

# Recovers key2 from a product committed by prime_gen.py.
#
# prime_gen.py writes pub.key as base64(str(key1 * key2)) and private.key as
# str(key1). Recovering key2 needs an EXACT integer division: the two factors
# here are up to 3072 and 2048 bits, and float division on numbers that size
# either overflows outright or rounds away the low bits, so this must use //
# and confirm there was no remainder rather than / and trust the float.
def main():
    try:
        pub_data = Path("pub.key").read_text(encoding="utf-8").strip()
        decoded_bytes = base64.b64decode(pub_data)
        product = int(decoded_bytes.decode("utf-8"))

        priv_data = Path("private.key").read_text(encoding="utf-8").strip()
        divisor = int(priv_data)

        key, remainder = divmod(product, divisor)
        if remainder != 0:
            print("Error: private.key does not evenly divide pub.key, "
                  "so these files were not generated together.")
            return
        print(f"key: {key}")

    except FileNotFoundError as e:
        print(f"Error: Missing required key file - {e.filename}")
    except (ValueError, base64.binascii.Error) as e:
        print(f"Error: Invalid key format or data - {e}")
    except ZeroDivisionError:
        print("Error: Private key cannot be zero.")

if __name__ == "__main__":
    main()
