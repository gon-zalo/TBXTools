import sqlite3
import os
from pathlib import Path

class _SQLiteManager:
    '''
    Class to manage SQLite functions.
    '''

    def __init__(self):
        self.conn = None
        self.cur = None
        self.maxinserts = 10000

        self.punctuation = None

    def _check_extension(self, project_name): # adding .sqlite extension automatically
        file_name = Path(project_name)

        if file_name.suffix.lower() != '.sqlite':
            file_name = file_name.with_suffix('.sqlite')
        
        return file_name

    def create_project(self,project_name,overwrite=False):
        '''Opens a project. If the project already exists, it raises an exception. To avoid the exception use overwrite=True. To open existing projects, use the open_project method.'''

        project_name = self._check_extension(project_name)

        if os.path.isfile(project_name) and not overwrite:
                raise Exception("This project already exists. Use open_project().")
        
        else:
            if os.path.isfile(project_name) and overwrite:
                os.remove(project_name)

            self.conn = sqlite3.connect(project_name)

            with self.conn:
                self.cur = self.conn.cursor()
                self.cur.execute("CREATE TABLE sl_corpus(id INTEGER PRIMARY KEY AUTOINCREMENT, segment TEXT)")
                self.cur.execute("CREATE TABLE tl_corpus(id INTEGER PRIMARY KEY AUTOINCREMENT, segment TEXT)")
                self.cur.execute("CREATE TABLE parallel_corpus(id INTEGER PRIMARY KEY AUTOINCREMENT, segmentSL, segmentTL TEXT)")
                self.cur.execute("CREATE TABLE tagged_parallel_corpus(id INTEGER PRIMARY KEY, tagged_segmentSL, tagged_segmentTL TEXT)")
                self.cur.execute("CREATE TABLE sl_corpus_c(id INTEGER PRIMARY KEY AUTOINCREMENT, segment TEXT)")
                self.cur.execute("CREATE TABLE tl_corpus_c(id INTEGER PRIMARY KEY AUTOINCREMENT, segment TEXT)")
                self.cur.execute("CREATE TABLE sl_tagged_corpus(id INTEGER PRIMARY KEY AUTOINCREMENT, tagged_segment TEXT)")
                self.cur.execute("CREATE TABLE tl_tagged_corpus(id INTEGER PRIMARY KEY AUTOINCREMENT, tagged_segment TEXT)")
                self.cur.execute("CREATE TABLE sl_tagged_corpus_c(id INTEGER PRIMARY KEY AUTOINCREMENT, tagged_segment TEXT)")
                self.cur.execute("CREATE TABLE tl_tagged_corpus_c(id INTEGER PRIMARY KEY AUTOINCREMENT, tagged_segment TEXT)")
                self.cur.execute("CREATE TABLE sl_stopwords (id INTEGER PRIMARY KEY AUTOINCREMENT, sl_stopword TEXT)")
                self.cur.execute("CREATE TABLE sl_inner_stopwords (id INTEGER PRIMARY KEY AUTOINCREMENT, sl_inner_stopword TEXT)")
                self.cur.execute("CREATE TABLE tl_stopwords (id INTEGER PRIMARY KEY AUTOINCREMENT, tl_stopword TEXT)")
                self.cur.execute("CREATE TABLE tl_inner_stopwords (id INTEGER PRIMARY KEY AUTOINCREMENT, tl_inner_stopword TEXT)")
                self.cur.execute("CREATE TABLE sl_exclusion_regexps (id INTEGER PRIMARY KEY AUTOINCREMENT, sl_exclusion_regexp TEXT)")
                self.cur.execute("CREATE TABLE tl_exclusion_regexps (id INTEGER PRIMARY KEY AUTOINCREMENT, tl_exclusion_regexp TEXT)")
                self.cur.execute("CREATE TABLE sl_morphonorm_rules (id INTEGER PRIMARY KEY AUTOINCREMENT, sl_morphonorm_rule TEXT)")
                self.cur.execute("CREATE TABLE tl_morphonorm_rules (id INTEGER PRIMARY KEY AUTOINCREMENT, tl_morphonorm_rule TEXT)")
                self.cur.execute("CREATE TABLE evaluation_terms (id INTEGER PRIMARY KEY AUTOINCREMENT, sl_term TEXT, tl_term TEXT)")
                self.cur.execute("CREATE TABLE reference_terms (id INTEGER PRIMARY KEY AUTOINCREMENT, sl_term TEXT, tl_term TEXT)")
                self.cur.execute("CREATE TABLE validated_terms (id INTEGER PRIMARY KEY AUTOINCREMENT, sl_term TEXT, tl_term TEXT)")
                self.cur.execute("CREATE TABLE compoundify_terms_sl (id INTEGER PRIMARY KEY AUTOINCREMENT, term TEXT)")
                self.cur.execute("CREATE TABLE compoundify_terms_tl (id INTEGER PRIMARY KEY AUTOINCREMENT, term TEXT)")
                self.cur.execute("CREATE TABLE tsr_terms (id INTEGER PRIMARY KEY AUTOINCREMENT, term TEXT)")
                self.cur.execute("CREATE TABLE tosearch_terms (id INTEGER PRIMARY KEY AUTOINCREMENT, term TEXT)")
                self.cur.execute("CREATE TABLE exclusion_terms (id INTEGER PRIMARY KEY AUTOINCREMENT, sl_term TEXT, tl_term TEXT)")
                self.cur.execute("CREATE TABLE exclusion_noterms (id INTEGER PRIMARY KEY AUTOINCREMENT, sl_term TEXT, tl_term TEXT)")
                self.cur.execute("CREATE TABLE tokens (id INTEGER PRIMARY KEY AUTOINCREMENT, token TEXT, frequency INTEGER)")
                self.cur.execute("CREATE TABLE ngrams (id INTEGER PRIMARY KEY AUTOINCREMENT, ngram TEXT, n INTEGER, frequency INTEGER)")
                self.cur.execute("CREATE TABLE tagged_ngrams (id INTEGER PRIMARY KEY AUTOINCREMENT, ngram TEXT, tagged_ngram TEXT, n INTEGER, frequency INTEGER)")
                
                self.cur.execute("CREATE INDEX indextaggedngram on tagged_ngrams (ngram);")
                
                self.cur.execute("CREATE TABLE embeddings_sl (id INTEGER PRIMARY KEY AUTOINCREMENT, candidate TEXT, embedding BLOB)")
                self.cur.execute("CREATE INDEX indexembeddings_sl on embeddings_sl (candidate);")
                
                self.cur.execute("CREATE TABLE embeddings_sl_ref (id INTEGER PRIMARY KEY AUTOINCREMENT, candidate TEXT, embedding BLOB)")
                self.cur.execute("CREATE INDEX indexembeddings_sl_ref on embeddings_sl_ref (candidate);")
                
                self.cur.execute("CREATE TABLE embeddings_tl (id INTEGER PRIMARY KEY AUTOINCREMENT, candidate TEXT, embedding BLOB)")
                self.cur.execute("CREATE INDEX indexembeddings_tl on embeddings_tl (candidate);")
                
                self.cur.execute("CREATE TABLE term_candidates (id INTEGER PRIMARY KEY AUTOINCREMENT, candidate TEXT, n INTEGER, frequency INTEGER, measure TEXT, value FLOAT)")
                self.cur.execute("CREATE TABLE index_pt(id INTEGER PRIMARY KEY AUTOINCREMENT, source TEXT, target TEXT, probability FLOAT)")
                self.cur.execute("CREATE INDEX index_index_pt on index_pt (source);")
                self.cur.execute("CREATE TABLE linguistic_patterns (id INTEGER PRIMARY KEY AUTOINCREMENT, linguistic_pattern TEXT)")
                
                self.conn.commit()
                
    def open_project(self,project_name):
        '''Opens an existing project. If the project doesn't exist it raises an exception.'''

        project_name = self._check_extension(project_name)

        if not os.path.isfile(project_name):
                raise Exception("Project not found")
        else:
            self.conn = sqlite3.connect(project_name)
            self.cur = self.conn.cursor() 

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
            self.cur.executemany("INSERT INTO sl_stopwords (sl_stopword) VALUES (?)",data)  

    def insert_segments(self, data):
        with self.conn:
            self.cur.executemany("INSERT INTO sl_corpus (segment) VALUES (?)", data)

    def get_segments(self, corpus=None): # corpus in case we want to implement SL and TL
        segments = []

        with self.conn:
            self.cur.execute("SELECT segment from sl_corpus")

            for row in self.cur.fetchall():
                segment = row[0]
                segments.append(segment)
        
        return segments

    def insert_ngrams(self, data):
        with self.conn:
            self.cur.executemany("INSERT INTO ngrams (ngram, n, frequency) VALUES (?,?,?)", data)
    
    def insert_tokens(self, data):
        with self.conn:
            self.cur.executemany("INSERT INTO tokens (token, frequency) VALUES (?,?)", data)


    # get_ngrams
    # get_stopwords
    # get_corpus(table_name)
    # get_ngrams()
    # get_tokens()
    # get_stopwords(language)
    # get_inner_stopwords(language)
    # get_term_candidates()