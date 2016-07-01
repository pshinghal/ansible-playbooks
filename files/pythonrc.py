'''Setup Python REPL

Derived from https://gist.github.com/taavi223/1340876
'''

#######################
# IMPORTS & CONSTANTS #
#######################

import imp
import os
import sys
import re
import threading
import time

VIRTUAL_ENV = os.environ.get('VIRTUAL_ENV', None)
HOME = VIRTUAL_ENV or os.environ.get('WORKON_HOME', None) or os.environ['HOME']

#################################
# SAVE & RESTORE HISTORY STATES #
#################################

try:
    import readline
except ImportError:
    pass
else:

    ##################
    # TAB COMPLETION #
    ##################

    try:
        import rlcompleter
    except ImportError:
        pass
    else:
        if(sys.platform == 'darwin'):
            # Work around a bug in Mac OS X's readline module.
            readline.parse_and_bind("bind ^I rl_complete")
        else:
            readline.parse_and_bind("tab: complete")

    ######################
    # PERSISTENT HISTORY #
    ######################

    # Use separate history files for each virtual environment.
    HISTFILE = os.path.join(HOME, '.pyhistory')

    # Read the existing history if there is one.
    if os.path.exists(HISTFILE):
        try:
            readline.read_history_file(HISTFILE)
        except:
            # If there was a problem reading the history file then it may have
            # become corrupted, so we just delete it.
            os.remove(HISTFILE)

    # Set maximum number of commands written to the history file.
    readline.set_history_length(256)

    def savehist():
        try:
            readline.write_history_file(HISTFILE)
        except NameError:
            pass
        except Exception as err:
            print("Unable to save history file due to the following error: %s"
                  % err)

    # Register the ``savehist`` function to run when the user exits the shell.
    import atexit
    atexit.register(savehist)

#################
# COLOR SUPPORT #
#################

class TermColors(dict):
    """Gives easy access to ANSI color codes. Attempts to fall back to no color
    for certain TERM values. (Mostly stolen from IPython.)"""

    COLOR_TEMPLATES = (
        ("Black"       , "0;30"),
        ("Red"         , "0;31"),
        ("Green"       , "0;32"),
        ("Brown"       , "0;33"),
        ("Blue"        , "0;34"),
        ("Purple"      , "0;35"),
        ("Cyan"        , "0;36"),
        ("LightGray"   , "0;37"),
        ("DarkGray"    , "1;30"),
        ("LightRed"    , "1;31"),
        ("LightGreen"  , "1;32"),
        ("Yellow"      , "0;93"),
        ("BoldYellow"  , "1;33"),
        ("LightBlue"   , "1;34"),
        ("LightPurple" , "1;35"),
        ("LightCyan"   , "1;36"),
        ("White"       , "1;37"),
        ("Normal"      , "0"),
    )

    NoColor = ''

    def __init__(self):
        if os.environ.get('TERM') in ('xterm-color', 'xterm-256color', 'linux',
                                    'screen', 'screen-256color', 'screen-bce'):
            _base  = '\001\033[%sm\002'
            self.update(dict([(k, _base % v) for k,v in self.COLOR_TEMPLATES]))

        elif os.environ.get('TERM') in ('xterm',):
            _base  = '\033[%sm'
            self.update(dict([(k, _base % v) for k,v in self.COLOR_TEMPLATES]))

        else:
            self.update(dict([(k, self.NoColor) for k,v in self.COLOR_TEMPLATES]))
_c = TermColors()

################################
# PRETTY PRINT OUTPUT & ERRORS #
################################

# NOTE: there is a bug (at least on Mac OS X) that causes the following lines to
# garble the command history whenever there are long lines. Try enabling them
# and using the up/down arrows to cycle through your history.

# Make the prompts colorful.
sys.ps1 = "%s>>>%s" % (_c['LightGreen'], _c['Normal'])
sys.ps2 = "%s...%s" % (_c['LightPurple'], _c['Normal'])

# Enable pretty printing for STDOUT
def my_displayhook(value):
    if value is not None:
        # TODO: What's the point of this anyway?
        try:
            import __builtin__
            __builtin__._ = value
        except ImportError:
            __builtins__._ = value

        import pprint
        pprint.pprint(value)
        del pprint
sys.displayhook = my_displayhook

# Make errors and tracebacks stand out a bit more.
def my_excepthook(type, value, tb):
    sys.stderr.write(_c['Yellow'])
    import traceback
    output = traceback.print_exception(type, value, tb)
    del traceback
    sys.stderr.write(_c['Normal'])

    # NOTE: There is a bug (?) in Python 3, where a trailing color marker that's
    # written to STDERR or STDOUT by itself does not color the subsequent lines.
    # We work around this by manually calling ``flush`` afterwards.
    sys.stderr.flush()
sys.excepthook = my_excepthook
