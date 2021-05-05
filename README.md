# prime-keys
Utilises two large prime numbers to create a large number encoded in base64 with control over the seed needed to generate a random key.

# Commands
* python2 prime_gen.py (seed value) (options)
* '-gen': creates a random key.
* '-newkey': creates a prime key to encrypt.
* '-privatekey': creates a new private key.
* Having no seed values will defualt to the 'seed.txt' file.
* Having no options will defualt to the 'private.key','prime.key' and export to the 'pub.key' files
* only 1 option can be used at a time.
* seed is encoded in sha512 to avoid reversing the proccess.
