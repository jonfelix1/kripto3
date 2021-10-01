import codecs

N = 256
half_N = int(N/2)

class StreamCipher:
    def KSA(self, key):
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

    def PRGA(self, S1, S2):
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


    def get_keystream(self, key):
        S1, S2 = self.KSA(key)
        return self.PRGA(S1,S2)

    def encrypt_logic(self, key, text):
        key = [ord(c) for c in key]
        keystream = self.get_keystream(key)
        
        res = []
        for c in text:
            val = ("%02X" % (c ^ next(keystream)))  # XOR and taking hex
            res.append(val)
        return ''.join(res)

    def encrypt(self, key, plaintext):
        plaintext = [ord(c) for c in plaintext]
        return self.encrypt_logic(key, plaintext)

    def decrypt(self, key, ciphertext):
        ciphertext = codecs.decode(ciphertext, 'hex_codec')
        res = self.encrypt_logic(key, ciphertext)
        return codecs.decode(res, 'hex_codec').decode('utf-8')

    def manual_encrypt(self, key, plaintext):
        return self.encrypt(key, plaintext)

    def manual_decrypt(self, key, ciphertext):
        return self.decrypt(key, ciphertext)

    def file_encrypt(self, path, key):
        file = open(path)

        line = file.read().replace("\n", " ")
        file.close()

        return self.encrypt(key, line)

    def file_decrypt(self, path, key):
        file = open(path)

        line = file.read().replace("\n", " ")
        file.close()

        return self.decrypt(key, line)

if __name__ == '__main__':
    sc = StreamCipher()

    a = sc.manual_encrypt('key', 'lalalala')
    print(a) 
    print(sc.manual_decrypt('key',a)) 
       

    # print(sc.file_encrypt("plaintext.txt", "not-so-random-key"))
    # print(sc.file_decrypt("ciphertext.txt", "not-so-random-key"))