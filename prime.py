#!/usr/bin/env python
import base64
from pathlib import Path

def main():
    try:
        pub_data = Path("pub.key").read_text(encoding="utf-8").strip()
        decoded_bytes = base64.b64decode(pub_data)
        num = int(decoded_bytes.decode("utf-8"))
        
        priv_data = Path("private.key").read_text(encoding="utf-8").strip()
        divisor = int(priv_data)
        
        key = num / divisor
        print(f"key: {key}")
        
    except FileNotFoundError as e:
        print(f"Error: Missing required key file - {e.filename}")
    except (ValueError, base64.binascii.Error) as e:
        print(f"Error: Invalid key format or data - {e}")
    except ZeroDivisionError:
        print("Error: Private key cannot be zero.")

if __name__ == "__main__":
    main()