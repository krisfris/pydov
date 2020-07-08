import os
import json
import datetime
import appdirs
import pyxhook
import tendo.singleton

import config


me = tendo.singleton.SingleInstance()
logfile = os.path.join(config.datadir, 'keys.log')


def on_keyevent(event):
    d = {
        'window': event.WindowName,
        'process': event.WindowProcName,
        'key': event.Key,
        'action': event.MessageName,
        'date': datetime.datetime.now().isoformat(),
    }

    if isinstance(d['window'], bytes):
        d['window'] = d['window'].decode('utf-8')

    if d['process'] not in config.excluded_process_names and \
       d['window'] not in config.excluded_window_names:
        with open(logfile, 'a') as f:
            print(json.dumps(d), file=f)

def main():
    print(f'Writing to {logfile}')

    new_hook = pyxhook.HookManager()
    new_hook.KeyDown = on_keyevent
    new_hook.KeyUp = on_keyevent
    new_hook.HookKeyboard()
    new_hook.start()

if __name__ == '__main__':
    main()
