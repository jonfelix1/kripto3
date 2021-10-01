#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: @manojpandey

# Python 3 implementation for RC4 algorithm
# Brief: https://en.wikipedia.org/wiki/RC4

# Will use codecs, as 'str' object in Python 3 doesn't have any attribute 'decode'
import codecs

N = 256
half_N = int(N/2)

def KSA(key):
    K = key
    L = len(K)
    S1 = [0 for i in range(0, half_N)]
    S2 = [0 for i in range(0, half_N)]
    counter = 0

    for i in range(0, half_N):
        S1[i] = i
    
    for i in range(half_N, N):
        S2[i - half_N] = i
    
    j = 0
    for i in range(0, half_N):
        j = ((j + S1[(i + K[i % L]) % len(S1)]) % half_N + K[i % L] % half_N) % half_N
        S1[i], S1[j] = S1[j], S1[i]
    j = 0
    for i in range(0, half_N):
        j = ((j + S2[(i + K[i % L]) % len(S2)]) % half_N + K[i % L] % half_N) % half_N
        S2[i], S1[j] = S1[j], S2[i]

    return S1, S2

def PRGA(S1, S2):
    i = 0
    j1 = 0
    j2 = 0
    
    while True:
        i = (i + 1) % half_N
        j1 = (j1 + S1[i]) % half_N
    
        S1[i], S2[j1] = S2[j1], S1[i]  # swap values
        Z1 = S1[(S1[i] + S1[j1]) % half_N]
        yield Z1

        j2 = (j2 + S2[i]) % half_N
        S2[i], S1[j2] = S2[j2], S2[i]
        Z2 = S2[(S2[i]+ S2[j2]) % half_N]
        yield Z2


def get_keystream(key):
    S1, S2 = KSA(key)
    return PRGA(S1,S2)

def encrypt_logic(key, text):
    key = [ord(c) for c in key]
    keystream = get_keystream(key)
    
    res = []
    for c in text:
        val = ("%02X" % (c ^ next(keystream)))  # XOR and taking hex
        res.append(val)
    return ''.join(res)


def encrypt(key, plaintext):
    plaintext = [ord(c) for c in plaintext]
    return encrypt_logic(key, plaintext)


def decrypt(key, ciphertext):
    ciphertext = codecs.decode(ciphertext, 'hex_codec')
    res = encrypt_logic(key, ciphertext)
    return codecs.decode(res, 'hex_codec').decode('utf-8')

def manual_encrypt(key, plaintext):
    return encrypt(key, plaintext)

def manual_decrypt(key, ciphertext):
    return decrypt(key, ciphertext)

def file_encrypt(path, key):
    file = open(path)

    line = file.read().replace("\n", " ")
    file.close()

    return encrypt(key, line)

def file_decrypt(path, key):
    file = open(path)

    line = file.read().replace("\n", " ")
    file.close()

    return decrypt(key, line)

def main():
    print(file_encrypt("plaintext.txt", "not-so-random-key"))
    print(file_decrypt("ciphertext.txt", "not-so-random-key"))

if __name__ == '__main__':
    main()
