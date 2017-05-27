# -*- coding: utf-8  -*-
"""
Toolbox for anagrimes.

"""
# Same license as the other scripts from Pywikibot

import re
import sys
from warnings import warn
import unicodedata

class Atools(object):
    
    @classmethod
    def reverse_string(cls, string):
        #return  string.decode('utf8')[::-1].encode('utf8')
        return  string[::-1]

    @classmethod
    def strip_diacritics(cls, string):
        string = re.sub(u"œ", u"oe", string)
        no_diac = ''.join(c for c in unicodedata.normalize('NFD', string)
                                  if unicodedata.category(c) != 'Mn')
        return cls.remove_non_ascii(no_diac)

    @classmethod
    def alphagram(cls, string):
        return  ''.join(sorted(string))

    @classmethod
    def remove_non_ascii(cls, string):
        return "".join(char for char in string.lower() if ((ord(char) >= 97 and ord(char) <= 122) or (ord(char) >= 65 and ord(char) <= 90)))

