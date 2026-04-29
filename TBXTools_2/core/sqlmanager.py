
import os
import sqlite3
import string



class SQLiteManager:
     def __init__(self):
          self.conn= None
          self.cur= None
          self.maxinserts=10000
          self.punctuation= string.punctuation




     def create_project(self,project_name,overwrite=False):
        '''Opens a project. If the project already exists you have 2 options. With overwrite= True, it cancels the previous project and creates a new one. With overwrite= False it opens the existing project'''
        #lo cambié para dejar de tener que usar también la función open_project 
        if os.path.isfile(project_name) and overwrite:
                os.remove(project_name)
                

        
        
        self.conn=sqlite3.connect(project_name)

        
            
            
        with self.conn:
            self.cur = self.conn.cursor() #if not exists è perché altimenti crasha quando solo apre un progetto che gia`esiste e prova a creare cartelle che già esistono`
            self.cur.execute("CREATE TABLE IF NOT EXISTS corpus(id INTEGER PRIMARY KEY AUTOINCREMENT, segment TEXT)")
            self.cur.execute("CREATE TABLE IF NOT EXISTS stopwords (id INTEGER PRIMARY KEY AUTOINCREMENT, stopword TEXT)")
            self.cur.execute("CREATE TABLE IF NOT EXISTS inner_stopwords (id INTEGER PRIMARY KEY AUTOINCREMENT, inner_stopword TEXT)")
            self.cur.execute("CREATE TABLE IF NOT EXISTS exclusion_regexps (id INTEGER PRIMARY KEY AUTOINCREMENT, exclusion_regexp TEXT)")


    
            self.cur.execute("CREATE TABLE IF NOT EXISTS tokens (id INTEGER PRIMARY KEY AUTOINCREMENT, token TEXT, frequency INTEGER)")
            self.cur.execute("CREATE TABLE IF NOT EXISTS ngrams (id INTEGER PRIMARY KEY AUTOINCREMENT, ngram TEXT, n INTEGER, frequency INTEGER)")

                
        
                
            self.cur.execute("CREATE TABLE IF NOT EXISTS term_candidates (id INTEGER PRIMARY KEY AUTOINCREMENT, candidate TEXT, n INTEGER, frequency INTEGER, measure TEXT, value FLOAT)")
        
                

     
#per ora ho tolto il compoundify- tanto nella parte statistica non lo utilizzava

     def load_corpus(self,corpusfile, encoding="utf-8"): #per ora solo caricare corpus senza compoundify
        '''Loads a monolingual corpus and saves it in our database in the table sl_corpus It's recommended, but not compulsory, that the corpus is segmented (one segment per line). Use external tools to segment the corpus. A plain text corpus (not segmented), can be aslo used.'''

        with open(corpusfile,"r",encoding=encoding,errors="ignore") as file_corpus: #vedi se cambiare il nome alla variabile
            data=[]
            continserts=0 #è un contatore- quante righe ho accomulato prima di inserirle nel database
        #accumuli righe in memoria e poi quando arriva a un certo numero- fai execute many e le inserisci tutte insieme nel database
        #perché se le inserissi direttamente andrebbe lentissimo
        #se per esempio ho 100mila righe- dovrei fare 100mila query
            for line in file_corpus:
                line=line.rstrip()
                data.append([line])
                continserts+=1
                if continserts==self.maxinserts: 
                    with self.conn:
                        self.cur.executemany("INSERT INTO corpus (segment) VALUES (?)",data)
                    data=[] #qui mi fa il reset- e quindi riinizia a contare
                    continserts=0
            if data:
                with self.conn: #inserisce le righe rimaste che non hanno raggiunto self.maxinserts
                    self.cur.executemany("INSERT INTO corpus (segment) VALUES (?)",data)    
    


     def load_stopwords(self,fitxer,encoding="utf-8"): #fitxer è parametro della funzione- esiste solo durante la chiamata
        with open(fitxer,"r",encoding=encoding) as file_stopwords:
            data=[]
            for linia in file_stopwords: #già mi legge il file linea per linea non serve anche dire readline()
                data.append([linia.rstrip()]) #questo è perché:
                #se facessi solo linia.rstrip- mi restituirebbe una stringa
                #se faccio [linia.rstrip()]- allora diventa lista che contiene la stringa
                #poi se aggiunge la lista che contiene la stringa alla lista data= `[]`
                #questo perché sql si aspetta una sequenza di tuple o liste
        
        for punct in self.punctuation:
            data.append([punct])

        with self.conn:
            self.cur.executemany("INSERT INTO stopwords (stopword) VALUES (?)",data) 



    

     def load_inner_stopwords(self,archivo,encoding="utf-8"):
        with open(archivo,"r",encoding=encoding) as file_inner_stopwords:
            data=[]
            for linia in file_inner_stopwords:
                data.append([linia.rstrip()])    
        for punct in self.punctuation:
            data.append([punct])

        with self.conn:
            self.cur.executemany("INSERT INTO inner_stopwords (inner_stopword) VALUES (?)",data)  
     
     
     


     def load_exclusion_regexps(self,archivo,encoding="utf-8"):
        with open(archivo,"r",encoding=encoding) as file_regex:
            data=[]
            for linia in file_regex:
                data.append([linia.rstrip()])  

            
        with self.conn:
            self.cur.executemany('INSERT INTO exclusion_regexps (exclusion_regexp) VALUES (?)',data)



     def get_segments(self):
        with self.conn:
            self.cur.execute(f"SELECT segment FROM corpus")
            rows= self.cur.fetchall() 
#prende tutti i segmenti dal corpus
#poi dalla lista di tuple che erano li trasforma in stringhe
        segments=[]
        for row in rows:
            segments.append(row[0])
    
        return segments 


     def insert_ngrams(self, data):
        with self.conn:
            self.cur.executemany(
            "INSERT INTO ngrams (ngram, n, frequency) VALUES (?,?,?)",
            data
        )
            

     def insert_tokens(self, data):
         with self.conn:
             self.cur.executemany("INSERT INTO tokens (token, frequency) VALUES (?,?)",
            data
        )
             
     def get_stopwords(self):
        with self.conn:
            self.cur.execute("SELECT stopword FROM stopwords")
            return [row[0] for row in self.cur.fetchall()]
    
     def get_inner_stopwords(self):
         inner_stopwords= []
         with self.conn:
             self.cur.execute("SELECT inner_stopword FROM inner_stopwords")
             for i in self.cur.fetchall():
                 inner_stopwords.append(i[0])
         return inner_stopwords
             
     def get_candidate_terms_ngrams(self):
           with self.conn:
               self.cur.execute("SELECT ngram, n, frequency FROM ngrams order by frequency desc")
           return self.cur.fetchall() #ottengo una roba così ("machine learning", 2, 95)
         
     
     def insert_candidate_terms(self, data):
          with self.conn:
              self.cur.executemany("INSERT INTO term_candidates (candidate, n, frequency, measure, value) VALUES (?,?,?,?,?)",data)  
             
     def delete_term_candidates(self):
        '''Deletes the term candidates.'''
        with self.conn:
            self.cur.execute('DELETE FROM term_candidates')

#la seguente funzione mi permette di cambiare i parametri ogni volta che voglio selezionare cose da "term candidates"
     def get_from_candidate_terms(self, columns=None, order_by=None):
         cols_str = "*" if columns is None else ", ".join(columns)
         query = f"SELECT {cols_str} FROM term_candidates"

         if order_by:
             query += f" ORDER BY {order_by}"
         with self.conn:
            self.cur.execute(query)
            return self.cur.fetchall()
         
     
     def get_from_exclusion_regex(self):
         with self.conn:
             self.cur.execute("SELECT exclusion_regexp FROM exclusion_regexps")
         return self.cur.fetchall()
        
     def delete_candidate_with_condition(self, candidate):
        with self.conn:
            self.cur.execute(
            'DELETE FROM term_candidates WHERE candidate=?',
            (candidate,)
        )
            
     def save_term_candidate_archivo(self, outputfile, encoding="utf-8"):
        with self.conn:
            self.cur.execute('SELECT candidate FROM term_candidates')
            
            with open(outputfile, "w", encoding=encoding) as f:
                for candidate in self.cur.fetchall():
                    f.write(candidate[0] + "\n")
    
            

      
    