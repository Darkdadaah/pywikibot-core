# -*- coding: utf-8  -*-
"""
Objects representing a Wiktionary DB (in Anagrimes style).

"""
# Same license as the other scripts from Pywikibot

import re
import sys
from warnings import warn
import unicodedata

from sqlalchemy import create_engine
from sqlalchemy import exc
from sqlalchemy import Column, Index, DateTime, String, UnicodeText, Integer, Float, Boolean, ForeignKey, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import text

from anagrimes_tools import Atools
Base = declarative_base()


class BaseEntity(object):
    __table_args__ = {  
            'mysql_engine':          'InnoDB',
            'mysql_default charset': 'utf8mb4',
            'mysql_collate':         'utf8mb4_general_ci',
            }


class Article(Base, BaseEntity):
    __tablename__ = 'articles'
    a_artid       = Column(Integer, primary_key=True)
    a_title        = Column(String(255))
    a_title_r      = Column(String(255))
    a_title_flat   = Column(String(255))
    a_title_flat_r = Column(String(255))
    a_alphagram    = Column(String(255))

    errors  = relationship("Error",  back_populates='articles', cascade="all, delete")
    lexemes = relationship("Lexeme", back_populates='articles', cascade="all, delete")


Index('a_title_idx',        Article.a_title,        mysql_length=15)
Index('a_title_r_idx',      Article.a_title_r,      mysql_length=15)
Index('a_title_flat_idx',   Article.a_title_flat,   mysql_length=15)
Index('a_title_flat_r_idx', Article.a_title_flat_r, mysql_length=15)
Index('a_alphagram_idx',    Article.a_alphagram,    mysql_length=15)


class Lexeme(Base, BaseEntity):
    __tablename__ = 'lexemes'
    l_lexid       = Column(Integer, primary_key=True)
    l_artid       = Column(Integer, ForeignKey('articles.a_artid'))
    l_lang        = Column(String(32))
    l_type        = Column(String(64))
    l_genre       = Column(String(16))
    l_num         = Column(Integer)
    l_is_flexion  = Column(Boolean, index=True)
    l_is_locution = Column(Boolean, index=True)
    l_is_gentile  = Column(Boolean, index=True)
    l_rand        = Column(Float(precision=40), index=True)
    l_sigle       = Column(String(16), index=True)

    articles = relationship("Article", back_populates="lexemes")
    prons    = relationship("Pron",    back_populates='lexemes', cascade="all, delete")


Index('l_lang_idx',  Lexeme.l_lang,  mysql_length=3)
Index('l_type_idx',  Lexeme.l_type,  mysql_length=4)
Index('l_genre_idx', Lexeme.l_genre, mysql_length=4)
Index('l_sigle_idx', Lexeme.l_sigle, mysql_length=2)


class Pron(Base, BaseEntity):
    __tablename__ = 'prons'
    p_pronid      = Column(Integer, primary_key=True)
    p_lexid       = Column(Integer, ForeignKey('lexemes.l_lexid'))
    p_pron        = Column(String(255))
    p_pron_flat   = Column(String(255))
    p_pron_flat_r = Column(String(255))
    p_num         = Column(Integer)

    lexemes = relationship("Lexeme", back_populates="prons")


Index('p_pron_idx',        Pron.p_pron,        mysql_length=15)
Index('p_pron_flat_idx',   Pron.p_pron_flat,   mysql_length=15)
Index('p_pron_flat_r_idx', Pron.p_pron_flat_r, mysql_length=15)


class Error(Base, BaseEntity):
    __tablename__ = 'errors'
    id          = Column(Integer, primary_key=True)
    article_id  = Column(Integer, ForeignKey('articles.a_artid'), index=True)
    article     = relationship("Article", back_populates="errors")
    description = Column(UnicodeText)
    error_type  = Column(UnicodeText)

    articles = relationship("Article", back_populates="errors")


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
        self.from_zero = False
        self.lexid = 1
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
            connect_string = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8mb4'.format(db_con['mysql_user'], db_con['mysql_pass'], db_con['mysql_host'], db_con['mysql_port'], db_con['mysql_db'])

            engine = create_engine(connect_string)
        session = sessionmaker()
        session.configure(bind=engine)
        Base.metadata.create_all(engine)
        db = session()
        #except Exception as e:
        #    raise Exception("Could not connect to the db: %s" % unicode(e))
        
        # Store the session and if the db was empty
        self.session = db
        if db.query(Meta).count() > 0:
            self.from_zero = False
            print "Updating DB"
        else:
            self.from_zero = True

            # Faster without foreign keys
            if self.db_type == 'mysql':
                db.execute("SET FOREIGN_KEY_CHECKS = 0")
    
    def define_language(self, lang):
        """
        Define the language of the project (e.g. frwiktionary)
        
        @param lang: wikimedia chapter code
        @type lang: Str
        """
        meta_lang = Meta(key=u'language', value=lang)
        db = self.session
        if self.from_zero:
            print "Init with language: %s" % lang
            db.add(meta_lang)
            db.commit()

    def add_articles(self, articles):
        db = self.session

        new_articles = []
        old_articles = []
        if not self.from_zero:
            for article in articles:
                artid = article.artid
                cur_lex = db.query(Lexeme).filter_by(l_artid = artid)
                if cur_lex:
                    cur_lex.update({"l_artid": None})
                    #db.flush()
                    self.add_errors(artid, article)
                    self.add_lexemes(artid, article)
                else:
                    raise Exception("Should be from zero, but found previous lexeme with artid=%d" % artid)
        else:
            for article in articles:
                self.add_article(article)

        
    def add_article(self, article):
        db = self.session
       # if not self.from_zero:
       #     del_art = db.query(Article).filter_by(a_artid=article.artid).all()
       #     if del_art:
       #         db.delete(del_art[0])
       #         db.flush()
        
        a_title        = article.title
        a_title_r      = Atools.reverse_string(article.title)
        a_title_flat   = Atools.strip_diacritics(article.title)
        a_title_flat_r = Atools.reverse_string(a_title_flat)
        a_alphagram    = Atools.alphagram(a_title_flat)
        art = Article(
                a_title        = a_title,
                a_title_r      = a_title_r,
                a_title_flat   = a_title_flat,
                a_title_flat_r = a_title_flat_r,
                a_alphagram    = a_alphagram,
                a_artid        = article.artid
                )
        self.session.add(art)
        self.add_errors(art.a_artid, article)
        self.add_lexemes(art.a_artid, article)
    
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
                    if sub_sec.tag == 'type' and sub_sec.attributes:
                        attr = sub_sec.attributes
                        rand = Atools.random()
                        lexeme = Lexeme(
                                l_artid      = article_id,
                                l_lang        = attr['lang'],
                                l_type        = attr['type'],
                                l_num         = attr['num'],
                                l_is_flexion  = attr['flex'],
                                l_is_locution = attr['loc'],
                                l_is_gentile  = attr['gentile'],
                                l_sigle       = attr['sigle'],
                                l_genre       = attr['genre'],
                                l_rand        = rand,
                                )
                        self.session.add(lexeme)

                        # Need to flush to get id
                        # OR generate the id without having to flush
                        l_lexid = self.get_lexid(lexeme)
                            
                        self.add_prons(l_lexid, sub_sec)

    def get_lexid(self, lexeme):
        if self.from_zero:
            self.lexid += 1
            return self.lexid
        else:
            self.session.flush()
            return lexeme.l_lexid
    
    def add_prons(self, lexeme_id, section):
        # Get list of prons
        prons = section.attributes["prons"]
        
        p_num = 1
        for pron_str in prons:
            p_pron_flat   = Atools.simple_pronunciation(pron_str)
            p_pron_flat_r = Atools.reverse_string(p_pron_flat)
            pron = Pron(
                    p_lexid = lexeme_id,
                    p_pron        = pron_str,
                    p_pron_flat   = p_pron_flat,
                    p_pron_flat_r = p_pron_flat_r,
                    p_num = p_num
                    )
            self.session.add(pron)
            p_num += 1

