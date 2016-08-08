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

from sqlalchemy import Column, DateTime, String, Integer, Boolean, ForeignKey, func
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import exc

Base = declarative_base()
class Page(Base):
    __tablename__ = 'page'
    id    = Column(Integer, primary_key=True)
    title = Column(String, unique=True)
    text  = Column(String)
    ns    = Column(String)
    # Use default=func.now() to set the default hiring time
    # of an Employee to be the current time when an
    # Employee record was created
    timestamp   = Column(DateTime)
    last_update = Column(DateTime, default=func.now())
    is_redirect = Column(Boolean, default=False)

def read_dump(dump_path, sqlite_path):
    # First, create SQLite DB
    db = create_db(sqlite_path)
    from_zero = (db.query(Page).count() == 0)
    
    # Then, parse the data and import in the DB
    xml = XMLDumpOldPageGenerator(dump_path)
    
    # Store pages
    n_pages = 0
    while True:
        try:
            page = next(xml.parser)
            page_to_db(db, page, from_zero)
            n_pages += 1
        except StopIteration:
            break
        if n_pages % 100000 == 0:
            pywikibot.output( u'%d pages' % n_pages )
            db.commit()
    db.commit()
    pywikibot.output( u'%d pages added or updated' % n_pages )

def create_db(sqlite_path):
    engine  = create_engine('sqlite:///' + sqlite_path)
    session = sessionmaker()
    session.configure(bind=engine)
    Base.metadata.create_all(engine)
    s = session()
    return s

def page_to_db(db, page_data, from_zero):
    time        = dateutil.parser.parse(page_data.timestamp)
    last_update = datetime.datetime.now()
    time        = time.replace(tzinfo=last_update.tzinfo)
    text        = page_data.text
    text.strip()
    new_page = Page(
            id          = page_data.id,
            title       = page_data.title,
            is_redirect = page_data.isredirect,
            text        = text,
            ns          = page_data.ns,
            timestamp   = time,
            last_update = last_update
            )
    if from_zero:
        db.add(new_page)
    else:
        db.merge(new_page)

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
        pywikibot.warning(u'No dump/sqlite file provided')

if __name__ == "__main__":
    main()

