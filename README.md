# prime-keys
Utilises two large prime numbers to create a large number encoded in base64 with control over the seed needed to generate a random key.

This is a factoring toy, not a proven encryption scheme: pub.key is just base64(str(key1 * key2)), and recovering key2 is a single exact division once you already hold key1. It demonstrates that multiplying two large primes together is one-way in practice (factoring the product back out is hard) but it is not RSA and should not be used to protect anything that actually matters.

# Commands
* python3 prime_gen.py [seed] [-gen | -newkey | -privatekey] [--bits N]
* '-gen': generates a random key from the seed only, writes nothing.
* '-newkey': creates a new prime.key.
* '-privatekey': creates a new private.key.
* '--bits N': bit size for the key being generated (default 2048 for prime.key, 3072 for private.key). Must be at least 16.
* Having no seed value defaults to the 'seed.txt' file, or system randomness if that is missing too.
* Having no options multiplies private.key by prime.key (generating prime.key first if it does not exist yet) and writes the product to pub.key.
* Only one of -gen/-newkey/-privatekey can be used at a time.
* The seed is hashed with sha512 before it seeds the random generator, so the same seed always reproduces the same key.
* python3 prime.py recovers key2 from an existing pub.key and private.key, and reports a mismatch instead of a wrong answer if the two files were not generated together.

# Testing
```
python3 -m unittest discover tests
```
