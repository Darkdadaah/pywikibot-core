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
        string = cls.replace_special_chars(string)
        no_diac = ''.join(c for c in unicodedata.normalize('NFD', string)
                                  if unicodedata.category(c) != 'Mn')
        return cls.remove_non_letter(no_diac)

    @classmethod
    def replace_special_chars(cls, string):
        pairs = [
                (u"œ", u"oe"),
                (u"Æ", u"AE"),
                (u"æ", u"ae"),
                (u"Œ", u"OE"),
                (u"œ", u"oe"),
                (u"ø", u"oe"),
                (u"&amp;", u""),
                (u"&quot;", u""),
                (u"‿", u" "),
                (u"…", u"..."),
                (u"_", u" "),
                ]
        for pair in pairs:
            string = re.sub(pair[0], pair[1], string)
        return string

    @classmethod
    def alphagram(cls, string):
        string = re.sub(' ', '', string)
        return  ''.join(sorted(string.lower()))

    @classmethod
    def remove_non_letter(cls, string):
        return "".join(char for char in string.lower() if (char.isalpha() or char == ' '))

