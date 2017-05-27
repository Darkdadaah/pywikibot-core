# -*- coding: utf-8  -*-
"""
Objects representing the structure of a French Wiktionary page.

"""
# Same license as the other scripts from Pywikibot
from __future__ import unicode_literals

import re
import sys
import textlib

from warnings import warn
from wiktionary_page import WiktArticleCommon
from wiktionary_page_fr_data import WiktData


class WiktArticle(WiktArticleCommon):
    """
    WiktArticle: Wiktionary article object.
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
                    section.attributes = { 'lang': pars["1"].strip() }
                elif name == u'caractère':
                    section.tag        = 'car'
                else:
                    raise Exception("Not a correct language template")
            except:
                error_msg = "[[%s]] Wrong lang section: '%s'" % (self.title, section.title)
                self.add_error('section_2', error_msg)
                return
        
        if section.level == 3:
            # Extract parameters
            try:
                template = self.parse_template(section.title)
                name = template[0]
                pars = template[1]
                sec_title = pars["1"].strip()
            
                # Detect what section it is
                normal_sec_title, sec_type = self.normalize_sec_title(sec_title)
                if (normal_sec_title):
                    section.tag = sec_type
                    if sec_type == 'type':
                        upper_lang = section.parent.attributes['lang']

                        # Parse form line
                        try:
                            form_line = WiktFormLine(section, self.title, upper_lang)
                            prons = form_line.get_prons()
                        except Exception as e:
                            error_msg = "[[%s]] Can't parse form line: '%s' (%s)" % (self.title, section.title, unicode(e))
                            self.add_error('form_line', error_msg)
                            return

                        # Store data for this section 
                        section.attributes = {
                                'lang': upper_lang,
                                'type': normal_sec_title,
                                'num': 1,
                                'flex': False,
                                'loc': False,
                                'prons': prons
                                }
                        
                        # Get num parameter
                        if "num" in pars:
                            section.attributes["num"] = pars["num"]
                        
                        # Check num parameter (for uniformity only)
                        if "2" in pars:
                            if pars["2"].strip() != upper_lang:
                                error_msg = "[[%s]] Different lang code: '%s' (section='%s' vs lang='%s')" % (self.title, section.title, pars["2"], upper_lang)
                                self.add_error('section_type', error_msg)
                                
                        if "3" in pars:
                            if pars["3"] == 'flexion':
                                section.attributes["flex"] = True
                            else:
                                error_msg = "[[%s]] Wrong par 3 (flexion) in type section: '%s'" % (self.title, section.title)
                                self.add_error('section_type', error_msg)
                
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
            raise Exception("[[%s]] Unknown section: '%s'" % (self.title, title))
        

class WiktFormLine(object):

    def __init__(self, section, title, lang):
        """
        Instantiate a lexeme form line object.
        
        @param title: title of the article
        @type title: Str
        @param text: text of the article
        @type text: Str
        """
        self.lang     = lang
        self.section  = section
        self.title    = title
        self.line_str = None
        self.data     = {}

    def get_form_line(self):
        if self.line_str:
            return self.line_str

        # We're looking for the form line
        for line in self.section.text:
            if line.startswith("'''"):
                self.line_str = line
                return
        raise Exception("No form line found")

    def parse(self):
        if self.data:
            return

        # Get the first line
        form_line = self.get_form_line()
        
        # Extract the templates on the line
        templates = textlib.extract_templates_and_params(self.line_str, True, True)

        # Get the interesting ones
        self.extract_prons_from_templates(templates)

    def extract_prons_from_templates(self, templates):
        prons = []
        for temp in templates:
            if temp[0] in ('pron', 'phon', 'phono'):
                args = temp[1]

                # Get pron string itself
                if "1" in args and args["1"].strip() != "":
                    pron_str = args["1"].strip()
                else:
                    continue

                if "2" in args and args["2"].strip() != "":
                    pron_lang = args["2".strip()]
                elif "lang" in args:
                    pron_lang = args["lang"]
                else:
                    raise Exception("No lang in pron template")

                # We have enough to keep this pron!
                prons.append(pron_str)

        self.data["prons"] = prons

    def get_prons(self):
        self.parse()
        return self.data["prons"]

