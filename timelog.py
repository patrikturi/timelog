import os
from datetime import datetime
import argparse
import pickle

SUPPORTED_COMMANDS = ['start', 'set', 'show', 'remove', 'switch', 'stop']
DATA_DIR_PATH = 'data'
TIME_ENTRIES_FILE_PATH = os.path.join(DATA_DIR_PATH, 'time_entries.p')


class TimeLog:

    def __init__(self):
        self.time_entries = None

        self.command_functions = {command_name: None for command_name in SUPPORTED_COMMANDS}
        self.command_functions['start'] = self.start_command
        self.command_functions['set'] = self.set_command
        self.command_functions['show'] = self.show_command

    def start_command(self, args):
        now = datetime.now()
        label = args.label if args.label else ''
        new_entry = {'date': now, 'label': label}
        self.time_entries.append(new_entry)

    def set_command(self, args):
        last_entry = self.time_entries[-1]
        if args.label:
            last_entry['label'] = args.label
        else:
            print('WARNING: "set" command had no effect, please specify parameters.')

    def show_command(self, args):
        for entry in self.time_entries:
            print(f'{entry["date"]} : {entry["label"]}')

    def load_data(self):
        if not os.path.isfile(TIME_ENTRIES_FILE_PATH):
            return None
        with open(TIME_ENTRIES_FILE_PATH, 'rb') as file:
            return pickle.load(file)

    def save_data(self, data):
        if not os.path.isdir(DATA_DIR_PATH):
            os.mkdir(DATA_DIR_PATH)
        with open(TIME_ENTRIES_FILE_PATH, 'wb') as file:
            pickle.dump(data, file)

    def main(self, command, args):

        data = self.load_data()
        self.time_entries = data if data else []

        if args.command not in self.command_functions:
            raise ValueError(f'Unkown command "{args.command}"')
        command_function = self.command_functions[command]
        if not command_function:
            raise NotImplementedError(f'Command "{command}" is not yet implemented')

        command_function(args)

        self.save_data(self.time_entries)


"""
Example display:
[1h] work1 (1:02)
[5m] work2 (2:12)
"""
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    commands = ', '.join(SUPPORTED_COMMANDS)
    parser.add_argument('command', help='Command to execute. Supported commands: {}'.format(commands))
    parser.add_argument('--label', '-l', help='Label of the activity being carried out')
    args = parser.parse_args()

    tl = TimeLog()
    tl.main(args.command, args)
