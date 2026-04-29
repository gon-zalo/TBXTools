
import string
import nltk
from nltk.util import ngrams
from nltk.probability import FreqDist
from .sqlmanager import SQLiteManager
import re




class StatisticalExtractor:
     def __init__(self):
      self.SLtokenizer=None #qui decideremo se ne vogliamo implementare uno di default
      self.specificSLtokenizer=False
      self.sqlmanager = SQLiteManager()


      
      
          





    #seguente codice- estrae ngrammi e frequenze dei token da un corpus memorizzato in database sql- poi salva in tabelle: ngrams e tokens
     def ngram_calculation (self,nmin,nmax,minfreq=2): #mifreq- soglia minima per salvare un n-gramma
        '''Performs the calculation of ngrams.'''
        ngramsFD=FreqDist()
        tokensFD=FreqDist()


        

        segments= self.sqlmanager.get_segments()

        for segment in segments:
            if self.specificSLtokenizer: 
                tokens=self.SLtokenizer(segment) 
            else:
                tokens=segment.split()
                    
                    #conto ngrammim
            for n in range(nmin,nmax+1):  #il +1 ´perché di base range esclude l'ultimo valore- il ciclo for scorre tutti i valori di n
                    for n_gram in ngrams(tokens,n):
                        ngramsFD[n_gram]+=1 #è contatore automatico di elementi
                    #conto tokens
            for token in tokens:
                tokensFD[token]+=1
                       
        n_gram_data=[]                
        for c in ngramsFD.most_common(): #ordina per frequenza decrescente
            if c[1]>=minfreq: #dalla tupla n gramma, frequenza- prende solo la frequenza
                record_ngram=[]
                record_ngram.append(" ".join(c[0]))    #prende la tupla e la trasforma in stringa        
                record_ngram.append(len(c[0])) #salva la lunghezza dell n gramma
                record_ngram.append(c[1])   #aggiunge la frequenza- quante volte appare
                n_gram_data.append(record_ngram)
            
        token_data=[]                
        for c in tokensFD.most_common():
            record_token=[]
            record_token.append(c[0])            
            record_token.append(c[1])   
            token_data.append(record_token)


        self.sqlmanager.insert_ngrams(n_gram_data)
        self.sqlmanager.insert_tokens(token_data)


      
     def statistical_term_extraction(self, minfreq=2):
        '''Performs a statistical term extraction using the extracted ngrams (ngram_calculation should be executed first). Loading stop-words is advisable. '''
        
        self.sqlmanager.delete_term_candidates()
        

        stopwords=self.sqlmanager.get_stopwords()
                
        inner_stopwords= self.sqlmanager.get_inner_stopwords()
        
        ngrammi= self.sqlmanager.get_candidate_terms_ngrams()
        data=[] 
        for a in ngrammi: #se prendo a`[0]`significa che prendo la stringa dell'n gramma
            #if self.specificSLtokenizer:
                #ng=self.SLtokenizer.tokenize(a[0]).split()
            #else:
                #ng=a[0].split()
            #controlla se ti toglie anche i punti interni oppure solo quelli alla fine
            #controlla anche se fa lo split o meno
            ng = re.findall(r"\b\w+\b", a[0].lower()) #tokenize the ngram string- lower case + extract word tokens using regex
            if not ng:
                continue

            include=True #presumiamo che il termina sia ok- poi se non soddisfa certe condizioni lo scartiamo
            if ng[0] in stopwords: #Excludes the term if the first word is a stopword
                include=False
            if ng[-1] in stopwords: #Excludes the term if the last word is a stopword
                include=False
            #for i in range(1,len(ng)): #salta prima parola e controlla dalla seconda in poi
                #if ng[i] in inner_stopwords:
                    #include=False
            for token in ng[1:]: #checks internal tokens
                if token in inner_stopwords:
                    include = False
                    break
            if include: #fai tupla invece di lista così non devi mettere tutti sti append e poi append della tupla alla lista
                record=[]
                record.append(" ".join(ng))  #stringa         
                record.append(a[1])   #n 
                record.append(a[2])   #frequenza in numero
                record.append("freq") 
                record.append(a[2])   #di nuovo frequenza- ma dopo freq
                data.append(record)
            if a[2]<minfreq: #Stops the loop if the frequency is below the threshold
                break
        self.sqlmanager.insert_candidate_terms(data)      


 


      
    