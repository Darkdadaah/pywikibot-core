# -*- coding: utf-8  -*-
"""
Objects representing the structure of a Wiktionary page, from the article to the meaning.

"""
# Same license as the other scripts from Pywikibot

import re
import sys
from warnings import warn

class WiktSection():
    
    def __init__(self, title, level, parent=None):
        """
        Instantiate a section object.
        
        @param title: title of the section
        @type title: Str
        """
        self.title        = title
        self.text         = []
        self.sub_sections = []
        self.level        = level
        self.parent       = parent
        
    def add_text(self, line):
        self.text.append(line)
    
    def add_sub_section(self, section):
        self.sub_sections.append(section)

class WiktArticle():
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
        self.title = title
        #self.text  = text
        self.lang  = lang
        self.top_section = self.parse_sections(text)

    def parse_sections(self, text):
        """
        Parse the wiki text in search of sections (started by == or section templates)
        """
        lines = text.split('\n')
        
        top_section = WiktSection(title='article', level=0)
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
                
                # Compare with the previous level
                if current_section.level > section_level:
                    # This is a subsection of the previous section
                    parent = levels[section_level - 1]
                elif current_section.level < section_level:
                    # Higher level: go back to the closest parent
                    parent = current_section
                
                current_section = WiktSection(title=title, parent=parent, level=section_level)
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
        print "SECTION (" + str(section.level) + ") = [ " + section.title + " ]"
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
        
