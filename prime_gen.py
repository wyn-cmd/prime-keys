#!/usr/bin/env python
import sys
import argparse
import random
import base64
import hashlib

# Pre-generated small primes for initial divisibility screening
SMALL_PRIMES = [
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71,
    73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151,
    157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233,
    239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313, 317,
    331, 337, 347
]

DEFAULT_KEY_BITS = 2048
DEFAULT_PRIVATE_BITS = 3072

# Generate a random integer in the range [2^(n-1)+1, 2^n-1]
def get_n_bit_random(n):
    return random.randrange(2**(n - 1) + 1, 2**n - 1)

# Generate a prime candidate not divisible by small pre-generated primes
def get_low_level_candidate(n):
    while True:
        pc = get_n_bit_random(n)
        for divisor in SMALL_PRIMES:
            if pc % divisor == 0 and divisor**2 <= pc:
                break
        else:
            return pc

# Run Miller-Rabin primality test with 18 iterations
def is_miller_rabin_passed(mrc):
    max_divisions_by_two = 0
    ec = mrc - 1
    while ec % 2 == 0:
        ec >>= 1
        max_divisions_by_two += 1

    def is_composite(round_tester):
        if pow(round_tester, ec, mrc) == 1:
            return False
        for i in range(max_divisions_by_two):
            if pow(round_tester, 2**i * ec, mrc) == mrc - 1:
                return False
        return True

    for _ in range(18):
        round_tester = random.randrange(2, mrc)
        if is_composite(round_tester):
            return False
    return True

# Search for a candidate until it passes Miller-Rabin
def generate_verified_prime(bits):
    while True:
        candidate = get_low_level_candidate(bits)
        if is_miller_rabin_passed(candidate):
            return candidate

# A positive integer of at least 16 bits, small enough that Miller-Rabin still
# means something and large enough that a candidate is worth searching for.
def bit_size(value):
    parsed = int(value)
    if parsed < 16:
        raise argparse.ArgumentTypeError("must be at least 16 bits")
    return parsed

def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Generate prime-based keys, or recover one with prime.py.")
    parser.add_argument("seed", nargs="?",
                         help="seed text; defaults to the contents of seed.txt")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-gen", action="store_true",
                        help="generate a random key from the seed only")
    group.add_argument("-newkey", action="store_true",
                        help="write a new prime.key")
    group.add_argument("-privatekey", action="store_true",
                        help="write a new private.key")
    parser.add_argument("--bits", type=bit_size, default=None,
                         help=f"bit size for -newkey/the default key "
                              f"(default {DEFAULT_KEY_BITS}) or -privatekey "
                              f"(default {DEFAULT_PRIVATE_BITS})")
    return parser.parse_args(argv)

def resolve_seed(seed_arg):
    if seed_arg is not None:
        return hashlib.sha512(seed_arg.encode("utf-8")).hexdigest()
    try:
        with open("seed.txt", "r", encoding="utf-8") as f:
            return hashlib.sha512(f.read().encode("utf-8")).hexdigest()
    except OSError:
        # No seed given and no seed.txt on disk: fall back to system
        # randomness rather than refusing to run.
        return hashlib.sha512(str(random.random()).encode("utf-8")).hexdigest()

def main(argv=None):
    args = parse_args(argv if argv is not None else sys.argv[1:])
    random.seed(int(resolve_seed(args.seed), 16))

    if args.gen:
        print('---------------------generating random key...---------------------')
        return

    if args.newkey:
        print('---------------------generating prime key...---------------------')
        prime = generate_verified_prime(args.bits or DEFAULT_KEY_BITS)
        with open('prime.key', 'w') as f:
            f.write(str(prime))
        print(prime)
        print('---------------------prime key generated...---------------------')
        return

    if args.privatekey:
        print('---------------------generating private key...---------------------')
        prime = generate_verified_prime(args.bits or DEFAULT_PRIVATE_BITS)
        with open('private.key', 'w') as f:
            f.write(str(prime))
        print(prime)
        print('---------------------private key generated...---------------------')
        return

    # Default: reuse prime.key as key2 if one already exists on disk, since
    # that lets a caller re-derive pub.key against a new private.key without
    # burning a fresh prime every time. Only generate one when there is none.
    try:
        with open('prime.key', 'r') as f:
            prime_candidate = int(f.read())
    except FileNotFoundError:
        prime_candidate = generate_verified_prime(args.bits or DEFAULT_KEY_BITS)
        with open('prime.key', 'w') as f:
            f.write(str(prime_candidate))

    try:
        with open('private.key', 'r') as f:
            key1 = int(f.read())
    except FileNotFoundError:
        print("Error: private.key not found.")
        sys.exit(1)

    key2 = prime_candidate
    product = str(key1 * key2)
    pub_key = base64.b64encode(product.encode('utf-8')).decode('utf-8')

    with open('pub.key', 'w') as f:
        f.write(pub_key)

    print(f'---------------------------start of key---------------------------\n{pub_key}\n----------------------------end of key----------------------------')

if __name__ == "__main__":
    main()
