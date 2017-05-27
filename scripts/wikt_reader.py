#!/usr/bin/python
# -*- coding: utf-8  -*-
r"""
Print a list of Wiktionary pages.

-dump:   path to a Mediawiki dump

&params;
"""
from __future__ import unicode_literals

import os
import re
import logging
import optparse
import datetime
import dateutil.parser

import pywikibot
from pywikibot.pagegenerators import XMLDumpOldPageGenerator
from pywikibot.xmlreader import XmlDump

from pywikibot.anagrimes_db import AnagrimesDB

Article = None

def read_dump(dump_path, db_con):
    # Parse the data
    xml = XMLDumpOldPageGenerator(dump_path)
    dump = XmlDump(dump_path)
    dump.parse_siteinfo()
    language = unicode(dump.siteinfo['lang'])
    global Article
    if language == 'frwiktionary':
        from pywikibot.wiktionary_page_fr import WiktArticle as Article
    elif language == 'enwiktionary':
        from pywikibot.wiktionary_page_en import WiktArticle as Article
    else:
        raise ValueError("Language %s is not supported" % language)
    
    # Then create the connection to the DB
    db = AnagrimesDB(db_con)
    db.create_db()
    db.define_language(language)
    
    # Store pages
    n_pages = 0
    while True:
        try:
            page = next(xml.parser)
            page_to_db(
                    db       = db,
                    page     = page,
                    language = language
                    )
            n_pages += 1
        except StopIteration:
            break
        if n_pages % 1000 == 0:
            pywikibot.output( u'%d pages' % n_pages )
            db.session.commit()
    db.session.commit()
    pywikibot.output( u'%d pages added or updated' % n_pages )

def page_to_db(db, page, language):
    # Create an article
    if page.ns == "0" and page.isredirect == False:
        text        = page.text
        text.strip()
    
        art = Article(
                title = unicode(page.title),
                text  = unicode(page.text),
                lang  = language
                )
        
        # Parse article
        art.tag_sections()
        
        # Store the article
        db.add_article(art)
        
        #art.print_sections()

def main(*args):
    """
    Process command line arguments and invoke bot.

    If args is an empty list, sys.argv is used.

    @param args: command line arguments
    @type args: list of unicode
    """
    local_args = pywikibot.handle_args(args)
    dump = None
    db_con = {}
    
    for arg in local_args:
        if arg.startswith('-dump:'):
            dump = arg[len('-dump:'):]
        if arg.startswith('-sqlite:'):
            db_con['sqlite_path'] = arg[len('-sqlite:'):]
        if arg.startswith('-mysql_user:'):
            db_con['mysql_user'] = arg[len('-mysql_user:'):]
        if arg.startswith('-mysql_pass:'):
            db_con['mysql_pass'] = arg[len('-mysql_pass:'):]
        if arg.startswith('-mysql_host:'):
            db_con['mysql_host'] = arg[len('-mysql_host:'):]
        if arg.startswith('-mysql_port:'):
            db_con['mysql_port'] = arg[len('-mysql_port:'):]
        if arg.startswith('-mysql_db:'):
            db_con['mysql_db'] = arg[len('-mysql_db:'):]
    
    if dump and db_con:
        read_dump(dump, db_con)
    else:
        pywikibot.warning(u'Need -dump and -sqlite to proceed')

if __name__ == "__main__":
    main()

