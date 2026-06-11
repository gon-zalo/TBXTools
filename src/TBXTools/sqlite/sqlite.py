import sqlite3
import os
from pathlib import Path
#import string #so far we are not using it- take it off in the final version


class SQLite:
    '''
    Manage SQLite functions.
    '''

    def __init__(self, stopwords, inner_stopwords, project_name, corpus=None, tagged_corpus=None, linguistic_patterns=None, evaluation_terms=None, exclusion_regexes=None, overwrite_project=False):
        self.cur = None
        self.MAX_INSERTS = 10000

        self.TABLES_TO_LOAD_AT_START = ["corpus", "tagged_corpus", "stopwords", "inner_stopwords", "linguistic_patterns", "evaluation_terms", "exclusion_regexes"]

    # Initializing project, corpus, stopwords, etc.
        self.initialize_project(project_name=project_name, overwrite_project=overwrite_project)
        self.load_data_to_tables(table_names=self.TABLES_TO_LOAD_AT_START, corpus=corpus, tagged_corpus=tagged_corpus, stopwords=stopwords, inner_stopwords=inner_stopwords, linguistic_patterns=linguistic_patterns, evaluation_terms=evaluation_terms, exclusion_regexes=exclusion_regexes)

    def add_extension(self, project_name):
        '''Adds the extension .sqlite to the database file.'''
        return Path(project_name).with_suffix('.sqlite')

    def initialize_project(self, project_name, overwrite_project):
        '''Initialize the SQLite project, either opening an existing one or creating a new one.'''
        file_name = self.add_extension(project_name=project_name)

        if file_name.exists() and overwrite_project==False:
            self.open_project(project_name=project_name)

        elif file_name.exists() and overwrite_project==True:
            self.create_project(project_name=project_name, overwrite=True)
        
        else:
            self.create_project(project_name=project_name)

    def create_project(self,project_name,overwrite=False):
        '''Opens a project. If the project already exists, it raises an exception. To avoid the exception use overwrite=True. To open existing projects, use the open_project method.'''

        project_name = self.add_extension(project_name)
        print(f"Creating project: {project_name}")
        
        if os.path.isfile(project_name) and overwrite:
            os.remove(project_name)

        self.conn = sqlite3.connect(project_name)

        with self.conn:
            self.cur = self.conn.cursor()
            self.cur.execute("CREATE TABLE corpus(id INTEGER PRIMARY KEY AUTOINCREMENT, segment TEXT)")
            self.cur.execute("CREATE TABLE tokens (id INTEGER PRIMARY KEY AUTOINCREMENT, token TEXT, frequency INTEGER)")
            self.cur.execute("CREATE TABLE ngrams (id INTEGER PRIMARY KEY AUTOINCREMENT, ngram TEXT, n INTEGER, frequency INTEGER)")
            self.cur.execute("CREATE TABLE candidate_terms (id INTEGER PRIMARY KEY AUTOINCREMENT, candidate TEXT, n INTEGER, frequency INTEGER, measure TEXT, value FLOAT)")
            self.cur.execute("CREATE TABLE stopwords (id INTEGER PRIMARY KEY AUTOINCREMENT, stopword TEXT)")
            self.cur.execute("CREATE TABLE inner_stopwords (id INTEGER PRIMARY KEY AUTOINCREMENT, inner_stopword TEXT)")
            self.cur.execute("CREATE TABLE exclusion_regexes (id INTEGER PRIMARY KEY AUTOINCREMENT, exclusion_regex TEXT)")
            self.cur.execute("CREATE TABLE linguistic_patterns (id INTEGER PRIMARY KEY AUTOINCREMENT, linguistic_pattern TEXT)")
            self.cur.execute("CREATE TABLE tagged_ngrams (id INTEGER PRIMARY KEY AUTOINCREMENT, ngram TEXT, tagged_ngram TEXT, n INTEGER, frequency INTEGER)")
            self.cur.execute("CREATE TABLE tagged_corpus(id INTEGER PRIMARY KEY AUTOINCREMENT, tagged_segment TEXT)")
            self.cur.execute("CREATE TABLE evaluation_terms(id INTEGER PRIMARY KEY AUTOINCREMENT, evaluation_term TEXT)")

    def open_project(self,project_name):
        '''Opens an existing project. If the project doesn't exist it raises an exception.'''

        project_name = self.add_extension(project_name)
        print(f"Opening project: {project_name}")

        if not os.path.isfile(project_name):
                raise Exception("Project not found")
        else:
            self.conn = sqlite3.connect(project_name)
            self.cur = self.conn.cursor() 

    def read_corpus(self, corpus_file, encoding):
        '''Read a corpus file.'''
        data = []
        continserts = 0
        with open(corpus_file, "r", encoding=encoding, errors="ignore") as file:
            data = [(line.rstrip(),) for line in file]
            continserts += 1

            if continserts == self.MAX_INSERTS:
                self.insert_segments(data)
                data = []
                continserts = 0

            self.insert_segments(data)

    def read_tagged_corpus(self, corpus_file, encoding):
        '''Reads a file line by line and inserts it into the 'tagged_corpus' table.'''
        data = []
        continserts = 0 
        with open(corpus_file, "r", encoding=encoding, errors="ignore") as file:
            data = [(line.rstrip(),) for line in file]
            continserts += 1

            if continserts == self.MAX_INSERTS:
                self.insert_tagged_segments(data)
                data = []
                continserts = 0

            self.insert_tagged_segments(data)

    # LOAD METHODS
    
    def load_corpus(self, corpus, encoding="utf-8", corpus_is_tagged=False, compoundify=False, comp_symbol="▁"):

        if corpus is None:
            table_name = 'tagged_corpus' if corpus_is_tagged else 'corpus'
            print(f"No {table_name.replace('_', ' ')} provided. Skipping '{table_name}' table load.")
            return

        corpora_list = corpus if isinstance(corpus, list) else [corpus]

        for corpus_file in corpora_list:
            if corpus_is_tagged:
                self.read_tagged_corpus(corpus_file=corpus_file, encoding=encoding)
            else:
                self.read_corpus(corpus_file=corpus_file, encoding=encoding)

        status_prefix = "Tagged " if corpus_is_tagged else ""
        if isinstance(corpus, list):
            print(f"{len(corpus)} {status_prefix.lower()}corpora loaded")
        else:
            print(f"{status_prefix}Corpus loaded")


    def load_stopwords(self, stopwords , encoding="utf-8"):
        '''Load the stopwords into the database.
        
        Args:
        
            stopwords: A stopwords list or file.
        '''
        data=[]

        if isinstance(stopwords, set):
            data = [(word,) for word in sorted(stopwords)]
            print("Stopwords loaded")

        else:
            with open(stopwords, "r", encoding=encoding) as f:
                data = [(line.rstrip(),) for line in f]

            print("Stopwords loaded from file") 
        with self.conn:
            self.cur.executemany("INSERT INTO stopwords (stopword) VALUES (?)",data) 

    def load_inner_stopwords(self, inner_stopwords , encoding="utf-8"):
        '''Load the inner stopwords into the database.
        
        Args:
        
            stopwords: A inner stopwords list or file.
        '''
        data=[]
        
        if isinstance(inner_stopwords, set):
            data = [(word,) for word in sorted(inner_stopwords)]
            print("Inner stopwords loaded")

        else:
            with open(inner_stopwords, "r", encoding=encoding) as f:
                data = [(line.rstrip(),) for line in f]
            
            print("Inner stopwords loaded from file") 

        with self.conn:
            self.cur.executemany("INSERT INTO inner_stopwords (inner_stopword) VALUES (?)",data) 


    
    def load_linguistic_patterns(self, linguistic_patterns, encoding="utf-8"):

        data= []
        if linguistic_patterns:
            if isinstance(linguistic_patterns, list):
                data = [(linguistic_pattern,) for linguistic_pattern in linguistic_patterns]
                print("Linguistic Patterns loaded")
            else:
                with open(linguistic_patterns, "r", encoding=encoding) as f:
                    data = [(line.rstrip(),) for line in f]
                print("Linguistic Patterns loaded from file")

            
            with self.conn:
                self.cur.executemany("INSERT INTO linguistic_patterns (linguistic_pattern) VALUES (?)",data) 


    def load_evaluation_terms(self, evaluation_terms, encoding='utf-8'):
        '''Loads the evaluation terms for the automatic learning of POS patterns'''

        data= []

        if not evaluation_terms:
            print("No evaluation terms to load into the database")
            return 
        
        if isinstance(evaluation_terms, list):
            data = [(evaluation_term,) for evaluation_term in evaluation_terms]
            print("Evaluation terms loaded")

        else: 
            with open(evaluation_terms, "r", encoding=encoding) as f:
                data = [(line.rstrip(),) for line in f]        
            print("Evaluation terms loaded from file")

        with self.conn:
            self.cur.executemany('INSERT INTO evaluation_terms (evaluation_term) VALUES (?)',data)


    def load_exclusion_regexes(self, exclusion_regexes, encoding='utf-8'):
        '''Loads the exclusion regular expressions for the source language.'''
        data=[]
        if exclusion_regexes:
            if isinstance(exclusion_regexes, list):
                data = [(regex,) for regex in exclusion_regexes]

                print("Exclusion regexes loaded")
            else:
                with open(exclusion_regexes, "r", encoding=encoding) as f:
                    data = [(line.rstrip(),) for line in f]
                print("Exclusion regexes loaded from file")

            with self.conn:
                self.cur.executemany('INSERT INTO exclusion_regexes (exclusion_regex) VALUES (?)',data)


    # INSERT METHODS
    def insert_segments(self, data):
        '''Inserts the segmented corpus into the database.'''
        with self.conn:
            self.cur.executemany("INSERT INTO corpus (segment) VALUES (?)", data)

    def insert_tagged_segments(self, data):
        '''Inserts a batch of tagged segments into the tagged_corpus table.'''
        with self.conn:

            self.cur.executemany("INSERT INTO tagged_corpus (tagged_segment) VALUES (?)", data)

    def insert_ngrams(self, data):
        '''Inserts Ngrams into the database.'''
        if not self.table_is_populated("ngrams"):
            with self.conn:
                self.cur.executemany("INSERT INTO ngrams (ngram, n, frequency) VALUES (?,?,?)", data)

    def insert_tagged_ngrams(self, data):
        '''Inserts Tagged Ngrams into the database.'''
        if not self.table_is_populated("tagged_ngrams"):
            with self.conn:
                ngrams_data = [(row[0], row[2], row[3]) for row in data]
                self.cur.executemany("INSERT INTO ngrams (ngram, n, frequency) VALUES (?, ?, ?)", ngrams_data)

                self.cur.executemany("INSERT INTO tagged_ngrams (ngram, tagged_ngram, n, frequency) VALUES (?,?,?, ?)", data)
    
    def insert_tokens(self, data):
        '''Inserts tokens into the database'''
        if not self.table_is_populated("tokens"):
            with self.conn:
                self.cur.executemany("INSERT INTO tokens (token, frequency) VALUES (?,?)", data)

    def insert_candidate_terms(self, data):
        '''Inserts candidate terms into the database'''
        if not self.table_is_populated("candidate_terms"):
            with self.conn:
                self.cur.executemany("INSERT INTO candidate_terms (candidate, n, frequency, measure, value) VALUES (?,?,?,?,?)", data)
            
    def insert_filtered_candidate_terms(self, data):
        with self.conn:
            self.cur.executemany("INSERT INTO filtered_candidate_terms (candidate, n, frequency, measure, value) VALUES (?,?,?,?,?)", data)

    # GET METHODS
    def get_segments(self):
        '''Gets the segmented corpus as a list of segments from the database.'''
        segments = []
        with self.conn:
            self.cur.execute("SELECT segment from corpus")

            for row in self.cur.fetchall():
                segment = row[0]
                segments.append(segment)
        
        return segments
    
    def get_tagged_segments(self):
        '''Gets the tagged segmented corpus as a list of segments from the database.'''
        tagged_segments = []
        with self.conn:
            self.cur.execute("SELECT tagged_segment from tagged_corpus")

            for row in self.cur.fetchall():
                tagged_segment = row[0]
                tagged_segments.append(tagged_segment)
        
        return tagged_segments

    def get_stopwords(self):
        '''Gets the list of stopwords from the database'''
        stopwords = []
        with self.conn:
            self.cur.execute("SELECT stopword FROM stopwords")

            for stopword in self.cur.fetchall():
                stopwords.append(stopword[0])

        return stopwords
    
    def get_inner_stopwords(self):
        '''Gets the list of inner stopwords from the database'''
        inner_stopwords = []
        with self.conn:
            self.cur.execute("SELECT inner_stopword FROM inner_stopwords")

            for inner_stopword in self.cur.fetchall():
                inner_stopwords.append(inner_stopword[0])

        return inner_stopwords
    
    def get_ngrams(self):
        '''Gets the list of Ngrams from the database'''
        ngrams = []
        with self.conn:
            self.cur.execute("SELECT ngram, n, frequency FROM ngrams ORDER BY frequency DESC")

            for ngram_row in self.cur.fetchall():
                ngrams.append(ngram_row)

        return ngrams
       
    def get_tagged_ngrams(self, ngram_filter= None): 
        '''
        Retrieve the list of tagged n-grams from the database.
        If a filter is provided, it returns only the matching n-grams.
        Otherwise, it returns all n-grams ordered by frequency in descending order.
        '''
        tagged_ngrams = []
        with self.conn:
            if ngram_filter:
                self.cur.execute("SELECT tagged_ngram, n, frequency FROM tagged_ngrams WHERE ngram= ?", (ngram_filter,))
            else:
                self.cur.execute("SELECT tagged_ngram, n, frequency FROM tagged_ngrams ORDER BY frequency DESC")

            for tagged_ngram_row in self.cur.fetchall():
                tagged_ngrams.append(tagged_ngram_row)

        return tagged_ngrams

    def get_candidate_terms(self):
        '''Gets the list of candidate terms from the database'''
        candidate_terms = []
        with self.conn:
            self.cur.execute("SELECT candidate, n, frequency FROM candidate_terms ORDER BY frequency DESC")

            for candidates_row in self.cur.fetchall():
                candidate_terms.append(candidates_row)

        return candidate_terms
        
    def get_exclusion_regexes(self):
        '''Gets the list of exclusion regexes from the database'''
        regexes = []
        with self.conn:
            self.cur.execute("SELECT exclusion_regex FROM exclusion_regexes")

            for regexes_row in self.cur.fetchall():
                regexes.append(regexes_row)
        
        return regexes
    
    def get_linguistic_patterns(self):
        linguistic_patterns= []
        with self.conn:
            self.cur.execute("SELECT linguistic_pattern FROM linguistic_patterns")

            for lingpattern_row in self.cur.fetchall():
                linguistic_patterns.append(lingpattern_row)
        
        return linguistic_patterns
    
    def get_evaluation_terms(self):
        evaluation_terms= []
        with self.conn:
            self.cur.execute("SELECT evaluation_term FROM evaluation_terms")

            for evaluation_term_row in self.cur.fetchall():
                evaluation_terms.append(evaluation_term_row[0])

        return evaluation_terms

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

    def delete_linguistic_patterns(self):
        with self.conn:
            self.cur.execute('DELETE FROM linguistic_patterns')
            self.cur.execute("DELETE FROM sqlite_sequence WHERE name='linguistic_patterns'")


    def delete_candidate_terms(self):
        with self.conn:
            self.cur.execute("DELETE FROM candidate_terms")
            self.cur.execute("DELETE FROM sqlite_sequence WHERE name='candidate_terms'")

    def delete_specific_candidate_term(self, candidate):
        with self.conn:
            self.cur.execute("DELETE FROM candidate_terms WHERE candidate=?", (candidate,))

# ADD FUNCTIONS
    def add_stopwords(self, stopwords_list):
        '''Add stopwords to the database that do not exist already.'''
        current_stopwords = self.get_stopwords()
        data = []
        for stopword in stopwords_list:
            if stopword in set(current_stopwords):
                continue
            else:
                data.append((stopword,))
        
        with self.conn:
            self.cur.executemany("INSERT INTO stopwords (stopword) VALUES (?)",data) 

    def add_inner_stopwords(self, inner_stopwords_list):
        '''Add inner stopwords to the database that do not exist already.'''
        current_inner_stopwords = self.get_inner_stopwords()
        data = []
        for inner_stopword in inner_stopwords_list:
            if inner_stopword in set(current_inner_stopwords):
                continue
            else:
                data.append((inner_stopword,))
        
        with self.conn:
            self.cur.executemany("INSERT INTO inner_stopwords (inner_stopword) VALUES (?)",data) 

# CHECK FUNCTIONS
    def table_is_populated(self, table_name):
        '''Checks if a table in the database contains data.'''
        with self.conn:
            self.cur.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = self.cur.fetchone()[0]
            if count > 0:
                return True
            else:
                return False
            
    def load_data_to_tables(self, table_names, corpus, tagged_corpus, stopwords, inner_stopwords, linguistic_patterns, evaluation_terms, exclusion_regexes):

        loaders = {
            "corpus": lambda: self.load_corpus(corpus=corpus, corpus_is_tagged=False),
            "tagged_corpus": lambda: self.load_corpus(corpus=tagged_corpus, corpus_is_tagged=True),
            "stopwords": lambda: self.load_stopwords(stopwords=stopwords),
            "inner_stopwords": lambda: self.load_inner_stopwords(inner_stopwords=inner_stopwords),
            "exclusion_regexes": lambda: self.load_exclusion_regexes(exclusion_regexes=exclusion_regexes),
            "linguistic_patterns": lambda: self.load_linguistic_patterns(linguistic_patterns=linguistic_patterns),
            "evaluation_terms": lambda: self.load_evaluation_terms(evaluation_terms=evaluation_terms)
        }

        for table in table_names:
            loader = loaders.get(table)
            # if the table does not have data, it is loaded in
            if loader and not self.table_is_populated(table_name=table):
                loader()

    
