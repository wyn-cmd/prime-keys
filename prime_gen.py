#!/usr/bin/env python
import sys,random,base64,binascii,hashlib
try:
    s=hashlib.sha512(sys.argv[1].encode('utf-8')).hexdigest()
except Exception:
    s=hashlib.sha512(open('seed.txt','r').read().encode('utf-8')).hexdigest()
seed=int(s,16)
random.seed()
random.seed(seed)
def nBitRandom(n):
    return(random.randrange(2**(n-1)+1,2**n-1))

# Pre generated primes
first_primes_list=[2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109,113,127,131,137,139,149,151,157,163,167,173,179,181,191,193,197,199,211,223,227,229,233,239,241,251,257,263,269,271,277,281,283,293,307,311,313,317,331,337,347]
  
def getLowLevelPrime(n):
    '''Generate a prime candidate divisible 
    by first primes'''
    while True:
        # Obtain a random number
        pc=nBitRandom(n) 
  
         # Test divisibility by pre-generated 
         # primes
        for divisor in first_primes_list:
            if pc%divisor==0 and divisor**2<=pc:
                break
        else:
            return pc
def isMillerRabinPassed(mrc):
    '''Run 20 iterations of Rabin Miller Primality test'''
    maxDivisionsByTwo = 0
    ec=mrc-1
    while ec%2==0:
        ec>>=1
        maxDivisionsByTwo+=1
    assert(2**maxDivisionsByTwo*ec==mrc-1)
  
    def trialComposite(round_tester):
        if pow(round_tester,ec,mrc)==1:
            return False
        for i in range(maxDivisionsByTwo):
            if pow(round_tester,2**i*ec,mrc)==mrc-1:
                return False
        return True
  
    # Set number of trials here
    numberOfRabinTrials=18
    for i in range(numberOfRabinTrials):
        round_tester=random.randrange(2,mrc)
        if trialComposite(round_tester):
            return False
    return True



try:
    if sys.argv[2]=='-gen':
        print('---------------------generating random key...---------------------')
    elif sys.argv[2]=='-newkey':
        print('---------------------generating prime key...---------------------')
        while True:
            n=2048
            prime_candidate=getLowLevelPrime(n)
            if not isMillerRabinPassed(prime_candidate):
                continue
            else:
                open('prime.key','w').write(str(prime_candidate))
                print(prime_candidate)
                print('---------------------prime key generated...---------------------')
                sys.exit()
    elif sys.argv[2]=='-privatekey':
        print('---------------------generating private key...---------------------')
        while True:
            n=3072
            prime_candidate=getLowLevelPrime(n)
            if not isMillerRabinPassed(prime_candidate):
                continue
            else:
                open('private.key','w').write(str(prime_candidate))
                print(prime_candidate)
                print('---------------------private key generated...---------------------')
                sys.exit()
    while True:
        n=2048
        prime_candidate=getLowLevelPrime(n)
        if not isMillerRabinPassed(prime_candidate):
            continue
        else:
            break
except Exception:
    prime_candidate=int(open('prime.key','r').read())

key1=int(open('private.key','r').read())

key2=prime_candidate

pub_key=str(base64.b64encode((str(key2*key1))).encode('utf-8')).decode('utf-8')
open('pub.key','w').write(pub_key)

print('---------------------------start of key---------------------------\n'+pub_key+'\n----------------------------end of key----------------------------')
