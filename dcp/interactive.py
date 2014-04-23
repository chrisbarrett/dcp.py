"""
Interactive commands for readnig from the terminal.
"""

import re

def read_number (prompt, default=None, read_fn=float):
    """Prompt the user for a number from stdin.

    prompt -- The prompt string to use.
    default -- An optional default value to use if no input is given.
    read_fn -- The function used to read the value into a number type.

    Returns:
    A number or the default value.
    """
    dflt = ' [{}]'.format(default) if default else ''
    line = input(prompt + dflt + ': ').strip()
    if not line:
        return default
    else:
        try:
            return read_fn(line)
        except ValueError:
            print('Invalid input')
            return read_number(prompt, default, read_fn)


def read_choice (prompt, choices, default=None):
    """Read a choice from the user.
    The input must match one of the choices in the `choices`.

    prompt -- A prompt to show the user.
    choices -- A list of choices to present to the user.
    default -- The default choice to use when no input is provided.

    Returns:
    The selected choice or the default value.
    """
    dflt = ' [{}]'.format(default) if default else ''
    line = input(prompt + dflt + ': ').strip()
    if not line:
        return default
    elif line in [str(c) for c in choices]:
        return line
    else:
        print('Invalid choice.')
        return read_choice(prompt, choices, default)


def read_y_or_n (prompt, default=False):
    """Prompt the user for a yes or no. Return True for y or False for n.
    """
    prompt_fmt = '{} [{}]: '.format(prompt, 'y' if default else 'n')
    line = input(prompt_fmt).strip().lower()
    if not line:
        return default
    elif re.match('^no?$', line):
        return False
    elif re.match('^y(es)?$', line):
        return True
    else:
        print('Must enter y or n')
        return read_y_or_n(prompt, default)
