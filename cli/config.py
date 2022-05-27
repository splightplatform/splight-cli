import io


class ConfigManager:

    def __init__(self, config_file: io.IOBase):
        self.config_file = config_file

    def load_config(self):
        assert(isinstance(self.config_file, io.IOBase))
        values = {}
        for line in self.config_file:
            line = line.rstrip('\n').split('#')[0]
            if line == '':
                continue
            (key, val) = line.rstrip('\n').split('=')
            values[key] = val
        return values

    def write_config(self, values: dict):
        assert(isinstance(self.config_file, io.IOBase))
        self.config_file.seek(0)
        for key, val in values.items():
            self.config_file.write(f'{key}={val}\n')
