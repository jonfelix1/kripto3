import wave

class AudioFile:
    
    def __init__(self, filename):
        self.filename = filename

    
    def read_frame(self):
        song = wave.open(self.filename, mode='rb')
        frame_bytes = bytearray(list(song.readframes(song.getnframes())))
        song.close()

        return frame_bytes

    def init_buff(self):
        song = wave.open(self.filename, mode='rb')
        init_buff = song.readframes(-1)
        init_buff = [item + 0 for item in init_buff]
        song.close()

        return init_buff

    def write(self, frame, params):
        song = wave.open(self.filename, mode='wb')
        song.setparams(params)
        song.writeframes(frame)
        song.close()

    def get_params(self):
        song = wave.open(self.filename, mode='rb')
        params = song.getparams()
        song.close()

        return params