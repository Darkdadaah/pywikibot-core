# -*- coding: utf-8  -*-
"""
Objects representing the structure of a French Wiktionary page.

"""
# Same license as the other scripts from Pywikibot

import re
import sys
from warnings import warn
from wiktionary_page import WiktArticleCommon

class WiktArticle(WiktArticleCommon):
    """
    WiktArticleFr: Wiktionary article object.
    """
    
    def __init__(self, title, text, lang):
        """
        Instantiate an article object from its title and text
        
        @param title: title of the article
        @type title: Str
        @param text: text of the article
        @type text: Str
        """
        WiktArticleCommon.__init__(self, title, text, lang);

    def rec_tag_sections(self, section):
        # FR specific section titles parsing
        if section.level == 2:
            # Extract the language code
            lang_search = re.search('^\{\{ *langue *\| *(.+?) *\}\}$', section.title)
            
            try:
                lang_code = lang_search.group(1)
            except:
                raise "No language code found for %s in %s" % (self.title, section.title)
            
            section.tag        = 'lang'
            section.attributes = { 'lang': lang_code }
        
        if section.level == 3:
            # Extract level 3
            sec_title_search = re.search('^\{\{ *S *\| *(.+?) *\}\}$', section.title)
            
            try:
                sec_title = sec_title_search.group(1)
            except:
                raise "No type code found for %s in %s" % (self.title, section.title)
            
            # Detect what section it is
            normal_sec_title = self.normalize_sec_title(sec_title);
            if (normal_sec_title):
                    section.tag        = 'type'
                    section.attributes = { 'type': normal_sec_title }
            
            section.tag        = 'type'
            section.attributes = { 'type': type_code }
            
        for sub_section in section.sub_sections:
            self.rec_tag_sections(sub_section)
    
