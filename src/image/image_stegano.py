# Assumed all data are in binary format
from PIL import Image
from math import log10, sqrt
import numpy as np
import random
import helper
import time


class SteganoImage:
    def __init__(self, cover_path, message_path, key):
        self.im = Image.open(cover_path, 'r')
        self.width = self.im.width
        self.height = self.im.height
        self.format = cover_path.split('.')[-1]
        self.mode = self.im.mode
        self.pixels = np.array(self.im.getdata(), dtype='uint8').ravel()

        with open(message_path, 'rb') as f:
            self.message = f.read()
        self.key = key

        self.data = b''
        self.stegoimage = None
        self.n = helper.determine_bytes(self.mode)

        self.seed = sum([ord(c) for c in key])

    def __del__(self):
        self.im.close()

    def encrypt(self, encrypt):
        if encrypt:
            bit = 1
            # StreamCipher
        else:
            bit = 0
        helper.change_bit(self.pixels[0], bit)

    def insert(self, encrypt=False, randomized=False):
        self.encrypt(encrypt)
        if randomized:
            helper.change_bit(self.pixels[1], 1)
            self.hide_data_random()
        else:
            helper.change_bit(self.pixels[1], 0)
            self.hide_data_seq()

    def extract(self):
        encrypt = self.pixels[0] & 1
        randomized = self.pixels[1] & 1
        if randomized:
            self.show_data_random()
        else:
            self.show_data_seq()

        if encrypt:
            # Decrypt with StreamCipher
            pass

    def compute_payload(self):
        return self.width * self.height * self.n  # In bits

    def compute_rms(self):
        # original = np.array(list(self.im.getdata()), dtype="int8").ravel()
        temp = np.copy(self.stegoimage).astype("int8")
        difference = self.pixels - temp
        return sqrt(1 / (self.width * self.height) * np.sum(difference ** 2))  # Multiply with the sigmas

    def compute_psnr(self):
        if self.stegoimage is None:
            return None
        rms = self.compute_rms()
        return 20 * log10(255 / rms)

    # DONE
    def hide_data_seq(self):
        bin_data = [format(b, '08b') for b in self.message]  # Bytes or bytearray
        len_data = len(bin_data)  # How many bytes
        total_len = len_data * 9  # File length with delimiters
        if total_len > self.compute_payload():
            print("File is too big")
            return
        count = 0
        new_pix = np.copy(self.pixels)
        for i, byte in enumerate(bin_data):
            for bit in byte:
                new_pix[i*9+2+count] = int(helper.change_bit(self.pixels[i*9+2+count], int(bit)))
                count += 1
            flag = 1 if i == len_data - 1 else 0
            new_pix[i*9+2+count] = int(helper.change_bit(self.pixels[i*9+2+count], flag))
            count = 0
        self.stegoimage = new_pix

    def hide_data_random(self):
        random.seed(self.seed)
        bin_data = [format(b, '08b') for b in self.message]  # Bytes or bytearray
        len_data = len(bin_data)  # How many bytes
        total_len = len_data * 9  # File length with delimiters
        if total_len > self.compute_payload():
            print("File is too big")
            return

        explored = []
        new_pix = np.copy(self.pixels)
        for i, byte in enumerate(bin_data):
            for bit in byte:
                new_pix[i * 9 + 2 + count] = int(helper.change_bit(self.pixels[i * 9 + 2 + count], int(bit)))
                count += 1
            flag = 1 if i == len_data - 1 else 0
            new_pix[i * 9 + 2 + count] = int(helper.change_bit(self.pixels[i * 9 + 2 + count], flag))
            count = 0
        self.stegoimage = new_pix

    # DONE
    def show_data_seq(self):
        data = b''
        bin_data = ''
        for i in range(2, len(self.pixels)):
            bin_data += str(self.pixels[i] & 1)
            if len(bin_data) // 9:
                char = int.to_bytes(int(bin_data[:8], 2), 1, byteorder='big')
                flag = bin_data[8]
                bin_data = bin_data[9:]
                data += char
                if flag == '1':
                    break
        self.data = data

    def show_data_random(self):
        random.seed(self.seed)
        data = b''
        bin_data = ''
        img_data = list(self.im.getdata())  # Array of pixels (tuples)
        if self.n == 1:
            img_data = [(pixel,) for pixel in img_data]

        pixel_count = {'i': 0, 'j': 0}
        explored = {}

        def count_index():
            return pixel_count['j'] * (pixel_count['i'] + 1)

        def generate_coordinate():
            while True:
                pixel_count['i'] = random.randint(0, self.height)
                pixel_count['j'] = random.randint(0, self.width)
                if pixel_count['i'] in explored:
                    if pixel_count['j'] not in explored[pixel_count['i']]:
                        explored[pixel_count['i']] = {pixel_count['j']: True}
                        break
                else:
                    explored[pixel_count['i']] = {pixel_count['j']: True}
                    break
            return img_data[count_index()]

        while True:
            pixel = generate_coordinate()
            for i in range(self.n):
                bin_data += str(pixel[i] & 1)
            if len(bin_data) // 9:
                char = int.to_bytes(int(bin_data[:8], 2), 1, byteorder='big')
                flag = bin_data[8]
                bin_data = bin_data[9:]
                data += char
                if flag == '1':
                    break
        self.data = data

    def save_stegoimage(self, path: str):
        if not path.endswith('.' + self.format):
            path += '.' + self.format
        if self.n == 1:
            image = Image.fromarray(self.stegoimage.ravel().reshape(self.height, self.width), mode=self.mode)
        else:
            image = Image.fromarray(self.stegoimage.ravel().reshape(self.height, self.width, self.n), mode=self.mode)
        image.save(path, self.format)

    def save_data(self, path: str):
        with open(path, 'wb') as f:
            f.write(self.data)


if __name__ == '__main__':
    s = SteganoImage('./flower.bmp', './message.txt', 'thisisakey')
    s.insert(encrypt=False, randomized=False)
    print(s.compute_psnr())
    s.save_stegoimage('./inserted')
    t = SteganoImage('./inserted.bmp', './message.txt', 'thisisakey')
    t.extract()
    t.save_data('./secret.txt')
    # check_file('./unnamed.png', './secret.png')
