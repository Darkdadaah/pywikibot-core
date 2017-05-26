# -*- coding: utf-8  -*-
"""
Objects representing the structure of a Wiki page.

"""
# Same license as the other scripts from Pywikibot

import re
import sys
from warnings import warn
from pywikibot import textlib

class WikiError():
    
    def __init__(self, description, error_type):
        """
        Instantiate an error object.
        
        """
        self.description = description
        self.error_type  = error_type

class WikiSection():
    
    def __init__(self, title, level, parent=None):
        """
        Instantiate a section object.
        
        @param title: title of the section
        @type title: Str
        """
        self.title        = title
        self.tag          = ""
        self.attributes   = {}
        self.text         = []
        self.sub_sections = []
        self.level        = level
        self.parent       = parent
        
    def add_text(self, line):
        self.text.append(line)
    
    def add_sub_section(self, section):
        self.sub_sections.append(section)

class WikiArticle():
    """
    WikiArticle: Wiki article object.
    """
    
    def __init__(self, title, text, lang):
        """
        Instantiate an article object from its title and text
        
        @param title: title of the article
        @type title: Str
        @param text: text of the article
        @type text: Str
        """
        self.title = title
        self.lang  = lang
        self.categories = []
        self.errors     = []
        self.top_section = self.parse_sections(text)
        
    def add_error(self, error_type, description):
        error = WikiError(description=description, error_type=error_type)
        self.errors.append(error)

    def parse_sections(self, text):
        """
        Parse the wiki text in search of sections (started by == or section templates)
        """
        lines = text.split('\n')
        
        top_section = WikiSection(title='article', level=0)
        current_section = top_section
        previous_section_level = 0
        levels = {
                0: top_section,
                1: top_section,
                2: top_section,
                3: top_section,
                4: top_section,
                5: top_section,
                6: top_section,
                }
        parent = None
        for line in lines:
            if line.startswith('='):
                # Determine the level
                if line.startswith('======'):
                    section_level = 6
                elif line.startswith('====='):
                    section_level = 5
                elif line.startswith('===='):
                    section_level = 4
                elif line.startswith('==='):
                    section_level = 3
                elif line.startswith('=='):
                    section_level = 2
                elif line.startswith('='):
                    section_level = 1
                
                # Extract title
                title = self._extract_title(line)
                if not title:
                    error_msg = "[[%s]] Section error '%s'" % (self.title, line)
                    self.add_error("section_parser", error_msg)
                    current_section.add_text(line)
                    continue
                
                # Compare with the previous level
                if current_section.level > section_level:
                    # This is a subsection of the previous section
                    parent = levels[section_level - 1]
                elif current_section.level < section_level:
                    # Higher level: go back to the closest parent
                    parent = current_section
                
                current_section = WikiSection(title=title, parent=parent, level=section_level)
                parent.add_sub_section(current_section)
                for i in range(section_level, 6):
                    levels[i] = current_section
            else:
                current_section.add_text(line)
        return top_section
    
    def _extract_title(self, line):
        title_search = re.search('^\s*=+\s*(.+?)\s*=+\s*$', line)
        
        if title_search:
            title = title_search.group(1)
            return title
        return
    
    def print_sections(self):
        if not self.top_section:
            self.parse_sections()
        self._rec_print_section(self.top_section)
    
    def _rec_print_section(self, section):
        attributes = map(lambda x: "%s=%s" % (x, section.attributes[x]), section.attributes.keys())
        print "SECTION %s-%s (%s) = [ %s ]" % (section.tag, ', '.join(attributes), str(section.level), section.title)
        if section.parent:
            print "SUBSECTION OF = [ " + section.parent.title + " ]"
        
        max = 0
        for line in section.text:
            print line
            max += 1
            if max >= 1:
                break
        for sub_section in section.sub_sections:
            self._rec_print_section(sub_section)

    def get_categories(self):
        """
        TODO: parse the texts to get the categories
        """
        return []
    
    def parse_template(self, template_str):
        templates = textlib.extract_templates_and_params(template_str, True, True)
        
        if len(templates) == 0:
            raise Exception("Not a template")
        elif len(templates) > 1:
            raise Exception("More than one template")
        else:
            return templates[0]

