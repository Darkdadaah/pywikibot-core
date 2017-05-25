# -*- coding: utf-8  -*-
"""
Objects representing the structure of a French Wiktionary page.

"""
# Same license as the other scripts from Pywikibot

import re
import sys
from warnings import warn
from wiktionary_page import WiktArticleCommon
from wiktionary_page_fr_data import WiktData


class WiktArticle(WiktArticleCommon):
    """
    WiktArticleFr: Wiktionary article object.
    """
    data = {}
    
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
                template = self.parse_template(section.title)
                name = template[0]
                pars = template[1]
                if name == 'langue':
                    section.tag        = 'lang'
                    section.attributes = { 'lang': pars["1"] }
                elif name == u'caractère':
                    section.tag        = 'car'
                else:
                    raise Exception("Not a correct language template")
            except:
                    error_msg = "Not a correct language section for '%s' in '%s'" % (self.title, section.title)
                    self.add_error('section_2', error_msg)
                    return
        
        if section.level == 3:
            # Extract parameters
            try:
                template = self.parse_template(section.title)
                name = template[0]
                pars = template[1]
                sec_title = pars["1"]
            
                # Detect what section it is
                normal_sec_title, sec_type = self.normalize_sec_title(sec_title)
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
                        
                        # Get num parameter
                        if "num" in pars:
                            section.attributes["num"] = pars["num"]
                        
                        # Check num parameter (for uniformity only)
                        if "2" in pars:
                            if pars["2"] != upper_lang:
                                error_msg = "Different language code in '%s' in '%s' (%s vs %s)" % (self.title, section.title, pars["2"], upper_lang)
                                self.add_error('section_type', error_msg)
                                
                        if "3" in pars:
                            if pars["3"] == 'flexion':
                                section.attributes["flex"] = True
                            else:
                                error_msg = "Wrong parameter 2 in '%s' in type section '%s'" % (self.title, section.title)
                                self.add_error('section_type', error_msg)
                
            except Exception as e:
                error_msg = "Wrong level 3 section format for '%s' in '%s'" % (self.title, section.title)
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
            raise Exception("Can't get data")
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
            raise Exception("Unrecognized type %s in %s" % (title, self.title))
    
