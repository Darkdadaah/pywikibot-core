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
     
    def normalize_sec_title(self, title):
        """
        Change the title to a standard name (may be wiki specific)
        
        @param title: section title
        @type title: Str
        """
        # In this common case, there is no standard
        return title
    
    def rec_tag_sections(self, section):
        # FR specific section titles parsing
        if section.level == 2:
            # Extract the language code
            try:
                lang_search = re.search('^\{\{ *langue *\| *(.+?) *\}\}$', section.title)
                lang_code = lang_search.group(1)
            except:
                if re.search(u"^\{\{ *caractère *\}\}$", section.title):
                    lang_code = 'caractere'
                else:
                    error_msg = "Not a correct language section for %s in %s" % (self.title, section.title)
                    self.add_error('section_2', error_msg)
                    return
            
            section.tag        = 'lang'
            section.attributes = { 'lang': lang_code }
        
        if section.level == 3:
            # Extract level 3
            sec_title_search = re.search('^\{\{ *S *\| *(.+?) *\}\}$', section.title)
            
            try:
                sec_title = sec_title_search.group(1)
            except:
                error_msg = "Not a correct type section for %s in %s (%d)" % (self.title, section.title, section.level)
                self.add_error('section_3', error_msg)
                return
            
            # Detect what section it is
            normal_sec_title = self.normalize_sec_title(sec_title);
            if (normal_sec_title):
                    section.tag        = 'type'
                    section.attributes = { 'type': normal_sec_title }
            
            section.tag        = 'type'
            section.attributes = { 'type': normal_sec_title }
            
        for sub_section in section.sub_sections:
            self.rec_tag_sections(sub_section)
    
