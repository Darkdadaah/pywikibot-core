# -*- coding: utf-8  -*-
"""
Objects representing a Wiktionary DB (in Anagrimes style).

"""
# Same license as the other scripts from Pywikibot

import re
import sys
from warnings import warn

from sqlalchemy import create_engine
from sqlalchemy import exc
from sqlalchemy import Column, Index, DateTime, String, UnicodeText, Integer, Boolean, ForeignKey, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class BaseEntity(object):
    __table_args__ = {  
            'mysql_engine': 'InnoDB',
            'mysql_default charset': 'utf8',
            'mysql_collate': 'utf8_bin',
            }

class Article(Base, BaseEntity):
    __tablename__ = 'article'
    id    = Column(Integer, primary_key=True)
    title = Column(String(256), index=True)
    #last_update = Column(DateTime, default=func.now())
    errors = relationship("Error", back_populates='article', cascade="all, delete, delete-orphan")
    lexemes = relationship("Lexeme", back_populates='article', cascade="all, delete, delete-orphan")

class Lexeme(Base, BaseEntity):
    __tablename__ = 'lexeme'
    id          = Column(Integer, primary_key=True)
    article_id  = Column(Integer, ForeignKey('article.id'), index=True)
    article     = relationship("Article", back_populates="lexemes")
    lang        = Column(String(32), index=True)
    type        = Column(String(64), index=True)
    num         = Column(Integer)
    flex        = Column(Boolean, index=True)
    loc         = Column(Boolean, index=True)

class Error(Base, BaseEntity):
    __tablename__ = 'error'
    id          = Column(Integer, primary_key=True)
    article_id  = Column(Integer, ForeignKey('article.id'), index=True)
    article     = relationship("Article", back_populates="errors")
    description = Column(UnicodeText)
    error_type  = Column(UnicodeText)

class Meta(Base, BaseEntity):
    __tablename__ = 'meta'
    id    = Column(Integer, primary_key=True)
    key   = Column(UnicodeText)
    value = Column(UnicodeText)
    timestamp   = Column(DateTime, default=func.now())

class AnagrimesDB():

    def __init__(self, db_con):
        """
        Instantiate an anagrimes DB (SQLite for now).
        
        @param path: path to the SQL db file
        @type path: Str
        """
        self.from_zero = True
        self.db_con = db_con
        if 'sqlite_path' in db_con:
            self.db_type = 'sqlite'
        elif 'mysql_db' in db_con:
            self.db_type = 'mysql'
        else:
            raise Exception("No proper DB connection provided")
        
    def commit(self):
        self.session.commmit()
    
    def create_db(self):
        """
        Create the schema of the database
        if the tables do not exist
        Also create the SQLite file if needed
        """
        #try:
        db_con = self.db_con
        if self.db_type == 'sqlite':
            engine  = create_engine('sqlite:///' + db_con['sqlite_path'])
        elif self.db_type == 'mysql':
            engine = create_engine("mysql+pymysql://%s:%s@%s/%s?host=%s?port=%s?charset=%s" % 
                        (db_con['mysql_user'],
                        db_con['mysql_pass'],
                        db_con['mysql_host'],
                        db_con['mysql_db'],
                        db_con['mysql_host'],
                        db_con['mysql_port'],
                        'utf8'
                        )
                    )
        session = sessionmaker()
        session.configure(bind=engine)
        Base.metadata.create_all(engine)
        db = session()
        #except Exception as e:
        #    raise Exception("Could not connect to the db: %s" % unicode(e))
        
        # Store the session and if the db was empty
        self.session = db
        self.from_zero = (db.query(Meta).count() == 0)
    
    def define_language(self, lang):
        """
        Define the language of the project (e.g. frwiktionary)
        
        @param lang: wikimedia chapter code
        @type lang: Str
        """
        meta_lang = Meta(key=u'language', value=lang)
        db = self.session
        if self.from_zero:
            db.add(meta_lang)
            db.commit()
        
    def add_article(self, article):
        db = self.session
        if not self.from_zero:
            del_art = db.query(Article).filter_by(title=article.title).all()
            if del_art:
                db.delete(del_art[0])
                db.flush()
        
        art = Article(title=article.title)
        self.session.add(art)
        self.session.flush()
        self.add_errors(art.id, article)
        self.add_lexemes(art.id, article)
    
    def add_errors(self, article_id, article):
        for error in article.errors:
            db_error = Error(article_id=article_id, description=error.description, error_type=error.error_type)
            self.session.add(db_error)
 
    def add_lexemes(self, article_id, article):
        # Get all type sections from the article
        start_sec = article.top_section
        
        for lang_sec in start_sec.sub_sections:
            # Language section
            if lang_sec.tag == 'lang':
                lang = lang_sec.attributes['lang']
                
                for sub_sec in lang_sec.sub_sections:
                    if sub_sec.tag == 'type':
                        attr = sub_sec.attributes
                        lexeme = Lexeme(
                                article_id = article_id,
                                lang = attr['lang'],
                                type = attr['type'],
                                num  = attr['num'],
                                flex = attr['flex'],
                                loc  = attr['loc'],
                                )
                        self.session.add(lexeme)
                        self.session.flush()
        
    
