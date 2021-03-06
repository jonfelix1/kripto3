import wave

class File:
    def __init__(self, filename):
        self.filename = filename

    def read_frame_audio_file(self):
        song = wave.open(self.filename, mode='rb')
        frame_bytes = bytearray(list(song.readframes(song.getnframes())))
        song.close()

        return frame_bytes

    def init_buff_audio_file(self):
        song = wave.open(self.filename, mode='rb')
        init_buff = song.readframes(-1)
        init_buff = [item + 0 for item in init_buff]
        song.close()

        return init_buff

    def write_audio_file(self, frame, params):
        song = wave.open(self.filename, mode='wb')
        song.setparams(params)
        song.writeframes(frame)
        song.close()

    def get_audio_params(self):
        song = wave.open(self.filename, mode='rb')
        params = song.getparams()
        song.close()

        return params

    def get_extention(self):
        has_extention = self.filename.split("/")[-1].find(".") != -1
        self.extension = ""

        if (has_extention):
            self.extension = self.filename.split(".")[-1]

        return self.extension

    def read_file(self):
        with open(self.filename, "rb") as f:
            byte_file = f.read()

        return byte_file

    def write_file(self, bytes_file):
        with open(self.filename, 'wb') as fd:
            fd.write(bytes_file)