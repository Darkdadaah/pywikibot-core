# -*- coding: utf-8  -*-
"""
Objects representing the structure of a Wiktionary page.

"""
# Same license as the other scripts from Pywikibot

import re
import sys
from warnings import warn
from wiki_page import WikiArticle

class WiktArticle(WikiArticle):
    """
    WiktArticle: Wiktionary article object.
    """
    
    def __init__(self, title, text, lang):
        """
        Instantiate an article object from its title and text
        
        @param title: title of the article
        @type title: Str
        @param text: text of the article
        @type text: Str
        """
        WikiArticle.__init__(self, title, text, lang);

