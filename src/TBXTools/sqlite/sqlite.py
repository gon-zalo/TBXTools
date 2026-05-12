import sqlite3
import os
from pathlib import Path
import string

class SQLite:
    '''
    Class to manage SQLite functions.
    '''

    def __init__(self):
        c = None
        self.cur = None
        self.maxinserts = 10000

        self.punctuation = string.punctuation
        self.stopwords = None
        self.inner_stopwords = None

    def check_extension(self, project_name): # adding .sqlite extension automatically
        file_name = Path(project_name)

        if file_name.suffix.lower() != '.sqlite':
            file_name = file_name.with_suffix('.sqlite')
        
        return file_name

    def create_project(self,project_name,overwrite=False):
        '''Opens a project. If the project already exists, it raises an exception. To avoid the exception use overwrite=True. To open existing projects, use the open_project method.'''

        project_name = self.check_extension(project_name)

        if os.path.isfile(project_name) and not overwrite:
                raise Exception("This project already exists. Use open_project().")
        
        else:
            if os.path.isfile(project_name) and overwrite:
                os.remove(project_name)

            self.conn = sqlite3.connect(project_name)

            with self.conn:
                self.cur = self.conn.cursor()
                self.cur.execute("CREATE TABLE corpus(id INTEGER PRIMARY KEY AUTOINCREMENT, segment TEXT)")
                self.cur.execute("CREATE TABLE tokens (id INTEGER PRIMARY KEY AUTOINCREMENT, token TEXT, frequency INTEGER)")
                self.cur.execute("CREATE TABLE ngrams (id INTEGER PRIMARY KEY AUTOINCREMENT, ngram TEXT, n INTEGER, frequency INTEGER)")
                self.cur.execute("CREATE TABLE candidate_terms (id INTEGER PRIMARY KEY AUTOINCREMENT, candidate TEXT, n INTEGER, frequency INTEGER, measure TEXT, value FLOAT)")
                self.cur.execute("CREATE TABLE filtered_candidate_terms (id INTEGER PRIMARY KEY AUTOINCREMENT, candidate TEXT, n INTEGER, frequency INTEGER, measure TEXT, value FLOAT)")
                self.cur.execute("CREATE TABLE stopwords (id INTEGER PRIMARY KEY AUTOINCREMENT, stopword TEXT)")
                self.cur.execute("CREATE TABLE inner_stopwords (id INTEGER PRIMARY KEY AUTOINCREMENT, inner_stopword TEXT)")
                self.cur.execute("CREATE TABLE exclusion_regexes (id INTEGER PRIMARY KEY AUTOINCREMENT, exclusion_regex TEXT)")


    def open_project(self,project_name):
        '''Opens an existing project. If the project doesn't exist it raises an exception.'''

        project_name = self.check_extension(project_name)

        if not os.path.isfile(project_name):
                raise Exception("Project not found")
        else:
            self.conn = sqlite3.connect(project_name)
            self.cur = self.conn.cursor() 


    # LOAD METHODS
    def load_stopwords(self, stopwords_file , encoding="utf-8"):
        data=[]
        record=[]
        with open(stopwords_file, "r", encoding=encoding) as fc:
            while 1:
                linia=fc.readline()
                if not linia:
                    break 
                linia=linia.rstrip()
                record.append(linia)
                data.append(record)
                record=[]
        
        for punct in self.punctuation:
            record.append(punct)
            data.append(record)
            record=[]

        with self.conn:
            self.cur.executemany("INSERT INTO stopwords (stopword) VALUES (?)",data)  
        
    def load_inner_stopwords(self, stopwords_file, encoding='utf-8'):
        data=[]
        record=[]
        with open(stopwords_file, "r", encoding=encoding) as fc:
            while 1:
                linia=fc.readline()
                if not linia:
                    break 
                linia=linia.rstrip()
                record.append(linia)
                data.append(record)
                record=[]
        
        for punct in self.punctuation:
            record.append(punct)
            data.append(record)
            record=[]

        with self.conn:
            self.cur.executemany("INSERT INTO inner_stopwords (inner_stopword) VALUES (?)",data)  

    def load_exclusion_regexes(self, exclusion_regexes_file, encoding='utf-8'):
        '''Loads the exclusion regular expressions for the source language.'''

        data=[]
        with open(exclusion_regexes_file, "r", encoding=encoding) as cf:
            for line in cf:
                line=line.rstrip()
                record=[]
                record.append(line)
                data.append(record)

        with self.conn:
            self.cur.executemany('INSERT INTO exclusion_regexes (exclusion_regex) VALUES (?)',data)

    # INSERT METHODS
    def insert_segments(self, data):
        with self.conn:
            self.cur.executemany("INSERT INTO corpus (segment) VALUES (?)", data)

    def insert_ngrams(self, data):
        with self.conn:
            self.cur.executemany("INSERT INTO ngrams (ngram, n, frequency) VALUES (?,?,?)", data)
    
    def insert_tokens(self, data):
        with self.conn:
            self.cur.executemany("INSERT INTO tokens (token, frequency) VALUES (?,?)", data)

    def insert_candidate_terms(self, data):
        with self.conn:
            self.cur.executemany("INSERT INTO candidate_terms (candidate, n, frequency, measure, value) VALUES (?,?,?,?,?)", data)
            
    def insert_filtered_candidate_terms(self, data):
        with self.conn:
            self.cur.executemany("INSERT INTO filtered_candidate_terms (candidate, n, frequency, measure, value) VALUES (?,?,?,?,?)", data)

    # GET METHODS
    def get_segments(self, corpus=None): # corpus in case we want to implement SL and TL
        segments = []
        with self.conn:
            self.cur.execute("SELECT segment from corpus")

            for row in self.cur.fetchall():
                segment = row[0]
                segments.append(segment)
        
        return segments

    def get_stopwords(self):
        stopwords = []
        with self.conn:
            self.cur.execute("SELECT stopword FROM stopwords")

            for stopword in self.cur.fetchall():
                stopwords.append(stopword[0])

        return stopwords
    
    def get_inner_stopwords(self):
        inner_stopwords = []
        with self.conn:
            self.cur.execute("SELECT inner_stopword FROM inner_stopwords")

            for inner_stopword in self.cur.fetchall():
                inner_stopwords.append(inner_stopword[0])

        return inner_stopwords
    
    def get_ngrams(self):
        ngrams = []
        with self.conn:
            self.cur.execute("SELECT ngram, n, frequency FROM ngrams ORDER BY frequency DESC")

            for ngram_row in self.cur.fetchall():
                ngrams.append(ngram_row)

        return ngrams

    def get_candidate_terms(self):
        candidate_terms = []
        with self.conn:
            self.cur.execute("SELECT candidate, n, frequency FROM candidate_terms ORDER BY frequency DESC")

            for candidates_row in self.cur.fetchall():
                candidate_terms.append(candidates_row)

        return candidate_terms
        
    def get_exclusion_regexes(self):
        regexes = []
        with self.conn:
            self.cur.execute("SELECT exclusion_regex FROM exclusion_regexes")

            for regexes_row in self.cur.fetchall():
                regexes.append(regexes_row)
        
        return regexes

    # DELETE METHODS
    def delete_corpus(self):
        with self.conn:
            self.cur.execute('DELETE FROM corpus')
            self.cur.execute("DELETE FROM sqlite_sequence WHERE name='corpus'")

    def delete_ngrams(self):
        with self.conn:
            self.cur.execute('DELETE FROM ngrams')
            self.cur.execute("DELETE FROM sqlite_sequence WHERE name='ngrams'")

    def delete_tokens(self):
        with self.conn:
            self.cur.execute('DELETE FROM tokens')
            self.cur.execute("DELETE FROM sqlite_sequence WHERE name='tokens'")

    def delete_candidate_terms(self):
        with self.conn:
            self.cur.execute("DELETE FROM candidate_terms")
            self.cur.execute("DELETE FROM sqlite_sequence WHERE name='candidate_terms'")

    def delete_specific_candidate_term(self, candidate):
        with self.conn:
            self.cur.execute("DELETE FROM candidate_terms WHERE candidate=?", (candidate,))