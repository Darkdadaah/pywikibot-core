# -*- coding: utf-8  -*-
"""
Objects representing the structure of a Wiktionary page.

"""
# Same license as the other scripts from Pywikibot

import re
import sys
from warnings import warn
from wiki_page import WikiArticle

class WiktArticleCommon(WikiArticle):
    """
    WiktArticleCommon: Wiktionary article object.
    """
    
    def __init__(self, title, text, lang, artid=None):
        """
        Instantiate an article object from its title and text
        
        @param title: title of the article
        @type title: Str
        @param text: text of the article
        @type text: Str
        """
        WikiArticle.__init__(self, title, text, lang, artid)
        
    def tag_sections(self):
        """
        Analyze the section titles to identify them
        For all Wiktionaries we will make the assumption that level 2 titles are 
        always language sections
        Identifying other types (word types in particular will have to be done
        with language specific analyzes)
        The type of language section is saved as a tag
        """
        # First, get all the language sections
        top = self.top_section
        
        # Then, look at the title of every section and change its tag accordingly
        self.rec_tag_sections(top)
       
    def rec_tag_sections(self, section):
        if section.level == 2:
            section.tag = 'lang'
        # This is a very simple version because it can only be used generically
        # Each language will need to reimplement this
            
        for sub_section in section.sub_sections:
            self.rec_tag_sections(sub_section)
    
    def normalize_sec_title(self, title):
        """
        Change the title to a standard name (may be wiki specific)
        
        @param title: section title
        @type title: Str
        """
        # In this common case, there is no standard
        return title
    
