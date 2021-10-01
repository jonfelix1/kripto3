import wave
import random
import base64
import sys
sys.path.append('../')

from audio.file import File
from stream_cipher import StreamCipher

class Inserter:

    def __init__(self, file_dir, message_dir, key):
        audio_file = File(file_dir)

        self.frame = audio_file.read_frame_audio_file()
        self.init_buff = audio_file.init_buff_audio_file()
        self.params = audio_file.get_audio_params()

        secret_message = File(message_dir)
        self.extension = secret_message.get_extention()
        self.message_string = ""

        byte_message = secret_message.read_file()
        self.message = base64.b64encode(byte_message).decode('utf-8')

        self.key = key

    def calc_seed(self):
        return sum([ord(i) for i in self.key])

    def encrypt_message(self, encrypt, key):
        if encrypt:
            sign = 1
            sc = StreamCipher()
            self.message_string = sc.manual_encrypt(key, self.message_string)
            # print(self.message_string)
        else:
            sign = 0

        self.frame[0] = self.frame[0] & 254 | sign

    def random_frame(self, randomize):
        if randomize:
            random.seed(self.seed)
            random.shuffle(self.frame_list)
            sign = 1
        else:
            sign = 0

        self.frame[1] = self.frame[1] & 254 | sign

    def modify_frame(self, array_bit):
        idx = 0
        for i in self.frame_list:
            if idx >= len(array_bit):
                break
            if i >= 2:
                self.frame[i] = self.frame[i] & 254 | array_bit[idx]
                idx += 1

    def insert_message(self, encrypt=False, randomize=False):
        self.seed = self.calc_seed()

        self.encrypt_message(encrypt, self.key)
        message_length = str(len(self.message) + len(self.extension) + 2)

        self.message_string = message_length + '[[' + self.extension + '[[' + self.message

        if 0.9 * len(self.frame) // 8 < len(self.message_string):
            raise ValueError("Ukuran pesan terlalu besar untuk audio")

        bits_map = map(int, ''.join([bin(ord(i)).lstrip('0b').rjust(8, '0') for i in self.message_string]))
        array_bit = list(bits_map)

        self.frame_list = list(range(len(self.frame)))
        self.random_frame(randomize)
        self.modify_frame(array_bit)

        return bytes(self.frame)

if __name__ == "__main__":
    insert = Inserter('../../sample/audio/suichan-wa-waarukunai-yo-nee.wav', 'text.txt', 'hoshimachi')
    frame_modified = insert.insert_message(encrypt=True,randomize=False)

    outfile_name = 'tes.wav'
    outfile = File(outfile_name)
    outfile.write_audio_file(frame_modified, insert.params)