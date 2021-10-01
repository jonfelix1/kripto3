# Assumed all data are in binary format
from PIL import Image
from math import log10, sqrt
import numpy as np
import random


def check_ext(path: str):
    return path.endswith('.png') or path.endswith('.bmp')


def determine_bytes(mode):
    length = len(mode)
    if length > 4:  # YCbCr
        return 3
    else:
        return length


def change_bit(value, bit):
    return (value & ~1) | bit


class SteganoImage:
    def __init__(self, path: str):
        if not check_ext(path):
            raise ValueError('File must be a .png or .bmp')
        self.im = Image.open(path, 'r')
        self.width = self.im.width
        self.height = self.im.height
        self.format = path.split('.')[-1]

        self.data = b''
        self.stegoimage = None
        self.n = determine_bytes(self.im.mode)

    def __del__(self):
        self.im.close()

    def compute_payload(self):
        return self.width * self.height * self.n  # In bits

    def compute_rms(self):
        original = np.array(list(self.im.getdata()), dtype="int8").reshape(self.height, self.width, self.n)
        temp = np.copy(self.stegoimage).astype("int8")
        difference = original - temp
        return sqrt(1/(self.width * self.height) * np.sum(difference**2))   # Multiply with the sigmas

    def compute_psnr(self):
        if self.stegoimage is None:
            return None
        rms = self.compute_rms()
        return 20 * log10(255/rms)

    # Assumed encrypted first
    def hide_data_seq(self, data: bytes):
        bin_data = [format(b, '08b') for b in data]  # Bytes or bytearray
        len_data = len(bin_data)  # How many bytes
        total_len = len_data * 9  # File length with delimiters
        if total_len > self.compute_payload():
            print("File is too big")
            return

        img_data = list(self.im.getdata())  # Array of pixels (tuples)
        count = 0
        pixel = img_data[0]
        pixel_count = 0
        new_pix = []
        for i, byte in enumerate(bin_data):
            for bit in byte:
                if count == self.n:
                    img_data[pixel_count] = tuple(new_pix)
                    pixel_count += 1
                    pixel = img_data[pixel_count]
                    count = 0
                    new_pix = []
                new_pix.append(int(change_bit(pixel[count], int(bit))))
                count += 1
            if count == self.n:
                img_data[pixel_count] = new_pix
                pixel_count += 1
                pixel = img_data[pixel_count]
                count = 0
                new_pix = []
            flag = 1 if i == len_data-1 else 0
            new_pix.append(int(change_bit(pixel[count], flag)))
            count += 1
        if len(new_pix) != self.n:
            for i in range(count, self.n):
                new_pix.append(img_data[pixel_count][i])
        img_data[pixel_count] = tuple(new_pix)

        np_arr = np.array(img_data, dtype='uint8').reshape(self.height, self.width, self.n)
        self.stegoimage = np_arr

    def hide_data_random(self, data, key, encrypt=False):
        random.seed(key)
        bin_data = [format(b, '08b') for b in data]  # Bytes or bytearray
        len_data = len(bin_data)
        total_len = len_data * 9
        if total_len > self.compute_payload():
            print("File is too big")
            return

        img_data = list(self.im.getdata())  # Array of pixels (tuples)
        count = 0
        pixel_count = {'i': 0, 'j': 0}
        explored = {}
        new_pix = []

        def count_index():
            return pixel_count['j'] * (pixel_count['i']+1)

        def generate_coordinate():
            while True:
                pixel_count['i'] = random.randint(0, self.height)
                pixel_count['j'] = random.randint(0, self.width)
                if pixel_count['i'] in explored:
                    if pixel_count['j'] not in explored[pixel_count['i']]:
                        explored[pixel_count['i']] = { pixel_count['j']: True }
                        break
                else:
                    explored[pixel_count['i']] = {pixel_count['j']: True}
                    break
            print(count_index())
            return img_data[count_index()]

        pixel = generate_coordinate()
        for i, byte in enumerate(bin_data):
            for bit in byte:
                if count == self.n:
                    img_data[count_index()] = tuple(new_pix)
                    pixel = generate_coordinate()
                    count = 0
                    new_pix = []
                new_pix.append(int(change_bit(pixel[count], int(bit))))
                count += 1
            if count == self.n:
                img_data[count_index()] = tuple(new_pix)
                pixel = generate_coordinate()
                count = 0
                new_pix = []
            flag = 1 if i == len_data - 1 else 0
            new_pix.append(int(change_bit(pixel[count], flag)))
            count += 1
        if len(new_pix) != self.n:
            for i in range(count, self.n):
                new_pix.append(pixel[i])
        img_data[count_index()] = tuple(new_pix)

        np_arr = np.array(img_data, dtype='uint8').reshape(self.height, self.width, self.n)
        self.stegoimage = np_arr

    def show_data_seq(self):
        data = b''
        bin_data = ''
        img_data = list(self.im.getdata())

        for pixel in img_data:
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

    def show_data_random(self, key):
        random.seed(key)
        data = b''
        bin_data = ''
        img_data = list(self.im.getdata())  # Array of pixels (tuples)

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
        if not path.endswith('.'+self.format):
            path += '.'+self.format
        image = Image.fromarray(self.stegoimage, mode=self.im.mode)
        image.save(path, self.format)

    def save_data(self, path: str):
        with open(path, 'wb') as f:
            f.write(self.data)

'''
def test_hide_image():
    stegano = SteganoImage('./cow.png')
    with open('./unnamed.png', 'rb') as f:
        img = f.read()
        stegano.hide_data_seq(img)
        stegano.save_stegoimage('./test-image.png')


def test_show_image():
    stegano = SteganoImage('./test-image.png')
    stegano.show_data_seq()
    stegano.save_data('./secret.png')


def test_hide_image_random():
    stegano = SteganoImage('./cow.png')
    with open('./unnamed.png', 'rb') as f:
        img = f.read()
        stegano.hide_data_seq(img)
        stegano.save_stegoimage('./test-image-random.png')


def test_show_image_random():
    stegano = SteganoImage('./test-image-random.png')
    stegano.show_data_seq()
    stegano.save_data('./secret.png')


def test_hide_text():
    stegano = SteganoImage('./cow.png')
    with open('./message.txt', 'rb') as f:
        img = f.read()
        stegano.hide_data_seq(img)
        stegano.save_stegoimage('./test-text.png')
        print(stegano.compute_psnr())


def test_show_text():
    stegano = SteganoImage('./test-text.png')
    stegano.show_data_seq()
    stegano.save_data('./secret.txt')


def test_hide_text_random():
    stegano = SteganoImage('./cow.png')
    with open('./message.txt', 'rb') as f:
        img = f.read()
        stegano.hide_data_random(img, 'key')
        stegano.save_stegoimage('./test-text-random.png')


def test_show_text_random():
    stegano = SteganoImage('./test-text-random.png')
    stegano.show_data_random('key')
    stegano.save_data('./secret.txt')


if __name__ == '__main__':
    test_hide_image_random()
    test_show_image_random()    # test_show_image()
    # check_file('./unnamed.png', './secret.png')
'''
