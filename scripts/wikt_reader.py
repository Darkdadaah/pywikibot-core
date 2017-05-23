#!/usr/bin/python
# -*- coding: utf-8  -*-
r"""
Print a list of Wiktionary pages.

-dump:   path to a Mediawiki dump

&params;
"""

import os
import re
import logging
import optparse
import datetime
import dateutil.parser

import pywikibot
from pywikibot.pagegenerators import XMLDumpOldPageGenerator
from pywikibot.xmlreader import XmlDump
from pywikibot.wiktionary_page_fr import WiktArticle

from sqlalchemy import create_engine
from sqlalchemy import exc
from sqlalchemy import Column, DateTime, String, Integer, Boolean, ForeignKey, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
class Meta(Base):
    __tablename__ = 'meta'
    id    = Column(Integer, primary_key=True)
    name  = Column(String, unique=True)
    timestamp   = Column(DateTime)

def create_db(sqlite_path):
    engine  = create_engine('sqlite:///' + sqlite_path)
    session = sessionmaker()
    session.configure(bind=engine)
    Base.metadata.create_all(engine)
    s = session()
    return s

def read_dump(dump_path, sqlite_path):
    # Parse the data
    xml = XMLDumpOldPageGenerator(dump_path)
    dump = XmlDump(dump_path)
    dump.parse_siteinfo()
    language = dump.siteinfo['lang']
    if language == 'frwiktionary':
        from pywikibot.wiktionary_page_fr import WiktArticle
    else:
        raise ValueError("Language %s is not supported" % language)
    
    # Then create the SQLite DB
    db = create_db(sqlite_path)
    from_zero = (db.query(Meta).count() == 0)
    
    # Store pages
    n_pages = 0
    while True:
        try:
            page = next(xml.parser)
            page_to_db(
                    db        = db,
                    page      = page,
                    from_zero = from_zero,
                    language  = language
                    )
            n_pages += 1
        except StopIteration:
            break
        if n_pages % 100000 == 0:
            pywikibot.output( u'%d pages' % n_pages )
            db.commit()
    db.commit()
    pywikibot.output( u'%d pages added or updated' % n_pages )

def page_to_db(db, page, from_zero, language):
    # Create an article
    if page.ns == "0" and page.isredirect == False:
        text        = page.text
        text.strip()
    
        art = WiktArticle(
                title = page.title,
                text  = page.text,
                lang  = language
                )
        
        # Store the article
        #art.add_to_db(db, from_zero);
        art.tag_sections();
        art.print_sections();
    #else:
    #    raise Exception("The end %s" % (page.title));

def main(*args):
    """
    Process command line arguments and invoke bot.

    If args is an empty list, sys.argv is used.

    @param args: command line arguments
    @type args: list of unicode
    """
    local_args = pywikibot.handle_args(args)
    dump = None
    sqlite = None
    
    for arg in local_args:
        if arg.startswith('-dump:'):
            dump = arg[len('-dump:'):]
        if arg.startswith('-sqlite:'):
            sqlite = arg[len('-sqlite:'):]
    
    if dump and sqlite:
        read_dump(dump, sqlite)
    else:
        pywikibot.warning(u'Need -dump and -sqlite to proceed')

if __name__ == "__main__":
    main()

