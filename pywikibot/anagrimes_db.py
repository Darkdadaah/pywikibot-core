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
from sqlalchemy import Column, DateTime, String, Integer, Boolean, ForeignKey, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Article(Base):
    __tablename__ = 'article'
    id    = Column(Integer, primary_key=True)
    title = Column(String, unique=True)
    last_update = Column(DateTime, default=func.now())
    errors = relationship("Error", back_populates='article', cascade="all, delete, delete-orphan")

class Error(Base):
    __tablename__ = 'error'
    id          = Column(Integer, primary_key=True)
    article_id  = Column(Integer, ForeignKey('article.id'))
    article     = relationship("Article", back_populates="errors")
    description = Column(String)
    error_type  = Column(String)

class Meta(Base):
    __tablename__ = 'meta'
    id    = Column(Integer, primary_key=True)
    key   = Column(String, unique=True)
    value = Column(String)
    timestamp   = Column(DateTime, default=func.now())

class AnagrimesDB():

    def __init__(self, path):
        """
        Instantiate an anagrimes DB (SQLite for now).
        
        @param path: path to the SQL db file
        @type path: Str
        """
        self.path = path
        self.from_zero = True
        
    def commit(self):
        self.session.commmit()
    
    def create_db(self):
        """
        Create the schema of the database
        if the tables do not exist
        Also create the SQLite file if needed
        """
        engine  = create_engine('sqlite:///' + self.path)
        session = sessionmaker()
        session.configure(bind=engine)
        Base.metadata.create_all(engine)
        db = session()
        
        # Store the session and if the db was empty
        self.session = db
        self.from_zero = (db.query(Meta).count() == 0)
    
    def define_language(self, lang):
        """
        Define the language of the project (e.g. frwiktionary)
        
        @param lang: wikimedia chapter code
        @type lang: Str
        """
        meta_lang = Meta(key='language', value=lang)
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
        return
    
