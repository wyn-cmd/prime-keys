#!/usr/bin/env python
import sys
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

def get_n_bit_random(n):
    """Generate a random integer in the range [2^(n-1)+1, 2^n-1]."""
    return random.randrange(2**(n - 1) + 1, 2**n - 1)

def get_low_level_candidate(n):
    """Generate a prime candidate that is not divisible by small pre-generated primes."""
    while True:
        pc = get_n_bit_random(n)
        for divisor in SMALL_PRIMES:
            if pc % divisor == 0 and divisor**2 <= pc:
                break
        else:
            return pc

def is_miller_rabin_passed(mrc):
    """Run Miller-Rabin primality test with 18 iterations."""
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

def generate_verified_prime(bits):
    """Keep searching for a candidate until it passes Miller-Rabin."""
    while True:
        candidate = get_low_level_candidate(bits)
        if is_miller_rabin_passed(candidate):
            return candidate

def main():
    # Seed initialization
    try:
        seed_str = sys.argv[1]
        s = hashlib.sha512(seed_str.encode('utf-8')).hexdigest()
    except IndexError:
        try:
            with open('seed.txt', 'r') as f:
                s = hashlib.sha512(f.read().encode('utf-8')).hexdigest()
        except Exception:
            # Fallback to system random if seed.txt is missing
            s = hashlib.sha512(str(random.random()).encode('utf-8')).hexdigest()

    random.seed(int(s, 16))

    try:
        flag = sys.argv[2]
        if flag == '-gen':
            print('---------------------generating random key...---------------------')
        elif flag == '-newkey':
            print('---------------------generating prime key...---------------------')
            prime = generate_verified_prime(2048)
            with open('prime.key', 'w') as f:
                f.write(str(prime))
            print(prime)
            print('---------------------prime key generated...---------------------')
            sys.exit()
        elif flag == '-privatekey':
            print('---------------------generating private key...---------------------')
            prime = generate_verified_prime(3072)
            with open('private.key', 'w') as f:
                f.write(str(prime))
            print(prime)
            print('---------------------private key generated...---------------------')
            sys.exit()
        
        # Default generation for key2
        prime_candidate = generate_verified_prime(2048)
    except (IndexError, Exception):
        with open('prime.key', 'r') as f:
            prime_candidate = int(f.read())

    # Key calculations
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