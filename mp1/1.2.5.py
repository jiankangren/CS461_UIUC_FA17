from Crypto.Util import number
from fractions import gcd
import multiprocessing
import sys

def iscoprime(a, b):
    return gcd(a, b) == 1

def isdivisible(a, b):
    return b % a == 0

e = 65537
def output_factors(p1, p2, q1, q2):
    outfileA = 'sol_1.2.5_factorsA.hex'
    outfileB = 'sol_1.2.5_factorsB.hex'
    with open(outfileA, 'w') as f:
        f.write(hex(p1)[2:]+'\n')
        f.write(hex(q1)[2:]+'\n')
        f.close()
    with open(outfileB, 'w') as f:
        f.write(hex(p2)[2:]+'\n')
        f.write(hex(q2)[2:]+'\n')
        f.close()

def getCRT(b1, b2, p1, p2):
    N = p1 * p2
    invOne = number.inverse(p2, p1)
    invTwo = number.inverse(p1, p2)
    return -(b1 * invOne * p2 + b2 * invTwo * p1) % N

def output_cert(p1, p2, q1, q2):
    import tweakedCertbuilder as cb
    from cryptography.hazmat.primitives.serialization import Encoding
    outfileA = 'sol_1.2.5_certA.cer'
    outfileB = 'sol_1.2.5_certB.cer'
    netid = 'hckuo2'
    privkey1, pubkey1 = cb.make_privkey(p1, q1)
    certA = cb.make_cert(netid, pubkey1)

    privkey2, pubkey2 = cb.make_privkey(p2, q2)
    certB = cb.make_cert(netid, pubkey2)

    print 'A sig:', certA.signature.encode('hex')
    print 'B sig:', certB.signature.encode('hex')

    with open(outfileA, 'wb') as f:
        f.write(certA.public_bytes(Encoding.DER))
        f.close()

    with open(outfileB, 'wb') as f:
        f.write(certB.public_bytes(Encoding.DER))
        f.close()

def getCoprimes(bitsize, e=e):
    p1, p2 = -1, -1
    while p1 == p2:
        p1 = number.getStrongPrime(bitsize, e)
        p2 = number.getStrongPrime(bitsize, e)
        assert(gcd(e, p1-1)==1)
        assert(gcd(e, p2-1)==1)
    return p1, p2

def calculate(b1, b2):
    b1t, b2t = b1 << 1024, b2 << 1024
    i = 0
    found = False
    while True:
        name = multiprocessing.current_process().name
        print name, 'iteration #', i
        i += 1
        p1, p2 = getCoprimes(512)
        p1p2 = p1 * p2
        b0 = getCRT(b1t, b2t, p1, p2)
        k = 0
        while True:
            b = b0 + (k * p1p2)
            k = k + 1
            if b >= twoPowerToTenth:
                break
            n1, n2 = b1t + b, b2t + b
            q1, q2 = n1 / p1, n2 / p2
            if number.isPrime(q1) and number.isPrime(q2) and iscoprime(e, q1-1) and iscoprime(e, q2-1):
                print 'FOUND!'
                found = True
                break
        if found:
            break
    print 'p1', p1
    print 'q1', q1
    print 'p2', p2
    print 'q2', q2
    output_factors(p1, p2, q1, q2)
    output_cert(p1, p2, q1, q2)

if __name__=='__main__':
    b1file = sys.argv[1]
    b2file = sys.argv[2]
    pool_size = int(sys.argv[3])
    twoPowerToTenth = 1 << 1024
    with open(b1file, 'rb') as f:
        b1 = f.read()
        f.close()

    with open(b2file, 'rb') as f:
        b2 = f.read()
        f.close()
    b1 = int(b1.encode('hex'), 16)
    b2 = int(b2.encode('hex'), 16)
    pool = []
    for i in range(pool_size):
        p = multiprocessing.Process(target=calculate, args=(b1,b2))
        print 'New Process', p.name
        pool.append(p)
    for p in pool:
        p.start()
    for p in pool:
        p.join()

