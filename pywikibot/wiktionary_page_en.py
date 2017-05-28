# -*- coding: utf-8  -*-
"""
Objects representing the structure of a French Wiktionary page.

"""
# Same license as the other scripts from Pywikibot
from __future__ import unicode_literals

import re
import sys
from warnings import warn
from wiktionary_page import WiktArticleCommon
from wiktionary_page_en_data import WiktData


class WiktArticle(WiktArticleCommon):
    """
    WiktArticle: Wiktionary article object.
    """
    data = {}
    
    def __init__(self, title, text, lang, artid=None):
        """
        Instantiate an article object from its title and text
        
        @param title: title of the article
        @type title: Str
        @param text: text of the article
        @type text: Str
        """
        WiktArticleCommon.__init__(self, title, text, lang, artid);
     
    def rec_tag_sections(self, section):
        # EN specific section titles parsing
        if section.level == 2:
            # Extract the language code
            try:
                name = section.title
                section.tag        = 'lang'
                section.attributes = { 'lang': name }
            except Exception as e:
                error_msg = "[[%s]] Wrong lang section: '%s' (%s)" % (self.title, section.title, unicode(e))
                self.add_error('section_2', error_msg)
                return

        elif section.level == 3:
            # Extract parameters
            try:
                # Detect what section it is
                normal_sec_title, sec_type = self.normalize_sec_title(section.title)
                if (normal_sec_title):
                    section.tag = sec_type
                    if sec_type == 'type':
                        upper_lang = section.parent.attributes['lang']
                        section.attributes = {
                                'lang': upper_lang,
                                'type': normal_sec_title,
                                'num': 1,
                                'flex': False,
                                'loc': False,
                                }
                        
            except Exception as e:
                error_msg = "[[%s]] Wrong section 3: '%s'" % (self.title, section.title)
                error_msg = error_msg + " (%s)" % (unicode(e))
                self.add_error('section_3', error_msg)
                return
        
        # Look at the subsections
        for sub_section in section.sub_sections:
            self.rec_tag_sections(sub_section)
    
    def normalize_sec_title(self, title):
        """
        Change the title to a standard name
        
        @param title: section title
        @type title: Str
        """
        lcfirst = lambda s: s[:1].lower() + s[1:]
        title = lcfirst(title)
        try:
            data = WiktData()
        except:
            raise Exception("Can't get sections list")
        word_types = data.word_types
        level3 = data.level3
        level4 = data.level4
        
        # Check if alias accepted
        if title in word_types:
            return word_types[title], 'type'
        elif title in level3:
            return level3[title], 'level3'
        elif title in level4:
            return level4[title], 'level4'
        else:
            raise Exception("[[%s]] Unknown section: '%s'" % (self.title, title))
    
