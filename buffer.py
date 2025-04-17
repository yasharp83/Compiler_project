class BufferedFileReader:
    def __init__(self, file_path="input.txt", buffer_size=1024):
        self.file_path = file_path
        self.buffer_size = buffer_size
        self.file = open(file_path, 'r', encoding='utf-8')
        self.buffer = ''
        self.pos = 0
        self.line = 1
        self.eof = False
        self._fill_buffer()

    def _fill_buffer(self):
        chunk = self.file.read(self.buffer_size)
        if chunk:
            self.buffer = chunk
            self.pos = 0
        else:
            self.eof = True
            self.buffer = ''
            self.pos = 0

    def has_next(self):
        if self.pos < len(self.buffer):
            return True
        if not self.eof:
            self._fill_buffer()
            return self.pos < len(self.buffer)
        return False

    def get_next_char(self):
        if not self.has_next():
            return False
        char = self.buffer[self.pos]
        current_line = self.line
        self.pos += 1

        if char == '\n':
            self.line += 1

        return char, current_line
    
    def check_next_char(self):
        if not self.has_next():
            return False
        char = self.buffer[self.pos]
        current_line = self.line
        return char , current_line

    def close(self):
        self.file.close()