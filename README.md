# prime-keys
Utilises two large prime numbers to create a large number encoded in base64 with control over the seed needed to generate a random key.

# Commands
* {python3 prime_gen.py (seed value) (options)}
*'-gen': creates a random key.
*'-newkey': creates a prime key to encrypt.
*'-privatekey': creates a new private key.
*having no seed valuse will defualt to the 'seed.txt' file.
*having no options will defualt to the 'private.key','prime.key' and export to the 'pub.key' files
