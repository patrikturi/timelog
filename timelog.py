import difflib
import os
from datetime import datetime
from datetime import timedelta
import argparse
import pickle


SUPPORTED_COMMANDS = ['start', 'set', 'show', 'remove', 'stop', 'start_fixed', 'start_existing,', 'start_ex']
DATA_DIR_PATH = 'data'
TIME_ENTRIES_FILE_PATH = os.path.join(DATA_DIR_PATH, 'time_entries.p')


class TimeLog:

    def __init__(self):
        self.time_entries = None

        self.command_functions = {command_name: None for command_name in SUPPORTED_COMMANDS}
        self.command_functions['start'] = self.start_command
        self.command_functions['set'] = self.set_command
        self.command_functions['show'] = self.show_command
        self.command_functions['stop'] = self.stop_command
        self.command_functions['start_fixed'] = self.start_fixed
        self.command_functions['start_existing'] = self.start_existing
        self.command_functions['start_ex'] = self.start_existing

    def start_command(self, args):
        self._stop_last_entry()
        self._start_new_entry(args.label)

    def stop_command(self, args):
        self._stop_last_entry()

    def start_existing(self, args):
        if not args.label:
            raise ValueError('Must specify a label for the start_existing command')
        labels = self._get_existing_labels()
        specified_label = args.label
        matches = difflib.get_close_matches(specified_label, labels)
        if len(matches) > 1:
            matches_str = ", ".join(matches)
            raise ValueError(f'Ambigious label, found matches: {matches_str}')
        elif len(matches) == 0:
            raise ValueError(f'No match for the specified label "{specified_label}"')
        else:
            matched_label = matches[0]

        self._stop_last_entry()
        self._start_new_entry(matched_label)

    def start_fixed(self, args):
        if not args.duration:
            raise ValueError('Must specify a duration for the start_fixed command')
        new_entry = self._start_new_entry(args.label)
        minutes = int(args.duration)
        new_entry['end'] = datetime.now() + timedelta(minutes=minutes)

    def set_command(self, args):
        if not self.time_entries:
            raise ValueError("Can't use \"set\" command when there are no time entries yet")
        last_entry = self.time_entries[-1]
        if args.label:
            last_entry['label'] = args.label
        else:
            print('WARNING: "set" command had no effect, please specify parameters.')

    def show_command(self, args):
        for entry in self.time_entries:
            end = entry.get('end') or datetime.now()
            time_diff = end - entry['start']
            time_diff_str = self._timedelta_to_str(time_diff)
            end_str = '   ' if entry.get('end') else ' --'
            print(f'{time_diff_str}{end_str} : {entry["label"]}')

    def _start_new_entry(self, label):
        if not label:
            label = ''
        return self._insert_entry(label)

    def _stop_last_entry(self):
        if len(self.time_entries) > 0:
            self._end_entry(self.time_entries[-1])

    def _get_existing_labels(self):
        return [entry['label'] for entry in self.time_entries if entry['label']]

    def _end_entry(self, entry):
        if not entry.get('end'):
            entry['end'] = datetime.now()

    def _insert_entry(self, label=''):
        now = datetime.now()
        new_entry = {'start': now, 'label': label}
        self.time_entries.append(new_entry)
        return new_entry

    def _timedelta_to_str(self, td):
        seconds = td.seconds
        seconds_to_next_min = 60 - td.seconds % 60
        if seconds_to_next_min < 60:
            seconds += seconds_to_next_min
        hours = seconds // 3600
        minutes = (seconds // 60) % 60
        hours_str = f'{hours}h ' if hours else ''
        minutes_str = f'{minutes}m ' if minutes else ''
        return f'{hours_str}{minutes_str}'

    def _is_running(self):
        if len(self.time_entries) == 0:
            return False
        last_entry = self.time_entries[-1]
        return bool(last_entry.get['end'])

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
    parser.add_argument('--duration', '-d', help='Specify a time duration in minutes')
    args = parser.parse_args()

    tl = TimeLog()
    tl.main(args.command, args)
