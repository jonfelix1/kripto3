from audio_file import AudioFile

class Extract:

    def __init__(self, file_dir, key):
        audio_file = AudioFile(file_dir)
        self.frame = audio_file.read_audio_frame
        self.key = key
        self.encrypted = bin(self.frame[0])[-1] == '1'
        self.randomized = bin(self.frame[1])[-1] == '1'

    def calc_seed(self):
        return sum([ord(i) for i in self.key])

    def extract_message(self):
        self.seed = self.calc_seed()
        extracted_arr = [self.frame[i] & 1 for i in range(len(self.frame))]

        # TODO: extract
