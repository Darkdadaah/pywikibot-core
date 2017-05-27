# -*- coding: utf-8  -*-
"""
Objects with data for the French Wiktionary

"""
# Same license as the other scripts from Pywikibot
from __future__ import unicode_literals

import re
import sys
from warnings import warn

class WiktData():
    """
    WiktData: Wiktionary data
    """
    word_types = {
            'adverb': 'adv',
            'ambiposition': 'ambipos',      # en specific
            'article': 'art',
            'circumposition': 'circumpos',  # en
            'classifier': 'class',
            'conjunction': 'conj',
            'contraction': 'contract',      # en
            'counter': 'count',             # en
            'determiner': 'det',
            'ideophone': 'ideo',            # en
            'interjection': 'interj',
            'noun': 'nom',
            'numeral': 'numeral',
            'participle': 'particip',       # en
            'particle': 'part',
            'postposition': 'post',
            'preposition': 'prep',
            'pronoun': 'pronom',
            'proper noun': 'nom-pr',
            'verb': 'verb',
            'circumfix': 'circumfix',       # en
            'combining form': 'combin',     # en
            'infix': 'inf',
            'interfix': 'interf',
            'prefix': 'pre',
            'root': 'root',                 # en
            'suffix': 'suff',
            'diacritical mark': 'diac',     # en
            'letter': 'letter',
            'ligature': 'ligature',         # en
            'number': 'number',             # en
            'punctuation mark': 'punct',    # en
            'syllable': 'syllable',         # en
            'symbol': 'symbol',
            'phrase': 'phr',
            'proverb': 'prov',
            'prepositional phrase': 'prep-phr', # en
            'character': 'car',             # en
            'hanzi': 'hanzi',               # en
            'kanji': 'kanji',               # en
            'hanja': 'hanja',               # en
            'brivla': 'brivla',             # en
            'cmavo': 'cmavo',               # en
            'gismu': 'gismu',               # en
            'lujvo': 'lujvo',               # en
            'rafsi': 'rafsi',               # en
            'romanization': 'romanization', # en
            }
            
    level3 = {
            'etymology': 'etym',
            'pronunciation': 'pron',
            'see also': 'voir',
            'anagrams': 'anagr',
            'references': 'ref',
            'trivia': 'trivia',
            'further reading': 'Further reading',
            }
    
    level4 = {
            }
