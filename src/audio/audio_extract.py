import wave
import random
import base64
import sys
sys.path.append('../')

from src.audio.file import File
from src.stream_cipher.stream_cipher import StreamCipher


class Extractor:
    def __init__(self, file_dir, key):
        stegano_audio_file = File(file_dir)
        self.frame = stegano_audio_file.read_frame_audio_file()
        self.key = key

    def calc_seed(self):
        return sum([ord(i) for i in self.key])

    def extract_messages(self):
        encrypted = bin(self.frame[0])[-1] == '1'
        random_frames = bin(self.frame[1])[-1] == '1'

        self.seed = self.calc_seed()
        extracted = [self.frame[i] & 1 for i in range(len(self.frame))]

        idx = 0
        mod_idx = 8

        message = ""
        temp = ""

        frame_list = list(range(len(extracted)))
        if random_frames:
            random.seed(self.seed)
            random.shuffle(frame_list)

        for i in frame_list:
            if i >= 2:
                if idx % mod_idx != (mod_idx - 1):
                    temp += str(extracted[i])
                else:
                    temp += str(extracted[i])
                    message += chr(int(temp, 2))
                    temp = ""

                idx += 1

        if encrypted:
            sc = StreamCipher()
            self.message_string = sc.manual_decrypt(self.key, message)
        else:
            self.message_string = message

    def parse_message(self):
        # print(self.message_string)
        message_info = self.message_string.split("$")

        self.message_length = int(message_info[0])
        self.extension = message_info[1]
        self.message = message_info[2]

    def get_secret_message(self):
        init = len(str(self.message_length)) + len(str(self.extension)) + 2
        decoded_bytes = self.message_string[init:init + self.message_length]
        bytes_file = decoded_bytes.encode('utf-8')

        return base64.b64decode(bytes_file)


if __name__ == "__main__":
    extract = Extractor('tes.wav', 'hoshimachi')
    extract.extract_messages()
    extract.parse_message()

    output_filename = 'output.txt'
    output_file = File(output_filename)
    byte = extract.get_secret_message()
    output_file.write_file(byte)