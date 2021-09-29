from audio_file import AudioFile
import random


class Insert:

    def __init__(self, file_dir, secret_message, key):
        audio_file = AudioFile(file_dir)

        self.frame = audio_file.read_audio_frame()
        self.init_buff = audio_file.init_buff_audio_file()
        self.params = audio_file.get_audio_params()

        self.secret_message = secret_message
        self.message = ""

        self.key = key

    def calc_seed(self):
        return sum([ord(i) for i in self.key])

    def encrypt_message(self, encrypted, key):
        if encrypted:
            sign = 1
            self.message = ""  # encrypt
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

    def insert_message(self, encrypted=False, randomize=False):
        self.seed = self.calc_seed()

        if 0.9 * len(self.frame) // 8 < len(self.string_message):
            raise ValueError("Ukuran pesan terlalu besar untuk audio")

        # TODO : insert
