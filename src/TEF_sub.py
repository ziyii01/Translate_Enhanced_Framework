import os
import sys

from TEF_log import log

class Sub:

    def splice_pathname(self):
        self.pathname = '.'.join([
            os.path.join(self.path, self.prefix),
            self.lang, self.suffix
        ])
    
    def split_pathname(self):
        self.path, filename = os.path.split(self.pathname)

        last_dot_index = filename.rfind('.')
        self.suffix = filename[last_dot_index+1 :]
        
        try:
            second_last_dot_index = filename.rindex('.', 0, last_dot_index)
        except:
            second_last_dot_index = None

        if second_last_dot_index:
            self.prefix = filename[: second_last_dot_index]
            self.lang = filename[second_last_dot_index+1 : last_dot_index]
        else:
            self.prefix = filename[: last_dot_index]
            self.lang = None



    def __init__(self, **vars):
        if 'pathname' in vars:
            self.pathname = vars['pathname']
            self.split_pathname()

        elif 'path' in vars and 'prefix' in vars and 'lang' in vars and 'suffix' in vars:
            self.path = vars['path']
            self.prefix = vars['prefix']
            self.lang = vars['lang']
            self.suffix = vars['suffix']
            self.splice_pathname()
        
        else:
            log.error("The class Sub init error")
            sys.exit()

    # ==
    def __eq__(self, other):
        if isinstance(other, Sub):
            return self.pathname == other.pathname
        return NotImplemented

    # <
    def __lt__(self, other):
        if isinstance(other, Sub):
            return self.pathname < other.pathname
        return NotImplemented

    # <=
    def __le__(self, other):
        return self < other or self == other

    # >
    def __gt__(self, other):
        return not self <= other

    # >=
    def __ge__(self, other):
        return not self < other

    # !=
    def __ne__(self, other):
        return not self == other
