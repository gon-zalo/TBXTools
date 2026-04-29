from .sqlmanager import SQLiteManager
import re


class Improvements:

    def __init__(self, sqlmanager): #qui glielo hai passato direttamente come argomento alla funzione- in teoria potresti fare lo stesso nella classe statistical extractor
        self.sqlmanager = sqlmanager


    def regex_exclusion(self, verbose=False): 
        regexs_results= self.sqlmanager.get_from_exclusion_regex()
        candidates= self.sqlmanager.get_from_candidate_terms(columns=["candidate"])
        
        if verbose:
            print(f"regex count: {len(regexs_results)}")
            print(f"candidates count: {len(candidates)}")
    
        deleted=0 #for debugging reasons
        for regex in regexs_results:
         #nregexp=len(r[0].split()) #conta quanti token ha la regex- lo tolgo ma chiedi
            regex_string=regex[0] #saves the regex as a string object
            regex_lista=re.compile(regex_string)
            for candidate in candidates:
                candidate_string=candidate[0]
            #ncandidate=len(candidate.split())
                match=regex_lista.match(candidate_string)
            
                if match:
                    self.sqlmanager.delete_candidate_with_condition(candidate_string)
                    deleted += 1
                    if verbose:
                        print(f"deleted: {candidate} (by {regex_string})")
        if verbose:
            print(f"total deleted: {deleted}")




    
#domanda su possibile miglioria!               
#il seguente codice funziona anche se magari si potrebbe implementare che poi le frequenze si sommano- come avviene per case_normalization
#percent=10: tolleranza per confrontare le frequenze (±10% di default)
    def nest_normalization(self,percent=10,verbose=False):
        '''
        Performs a normalization of nested term candidates. If an n-gram candidate A is contained in a n+1 candidate B and freq(A)==freq(B) or they are close values (determined by the percent parameter, A is deleted B remains as it is)
        '''
#Se un termine A (più corto) è contenuto in un termine B (più lungo)
#E hanno frequenze uguali o simili→ elimina A e mantiene B
        results= self.sqlmanager.get_from_candidate_terms(columns=["candidate", "n", "frequency"], order_by="frequency DESC")

        if verbose:
            print(f"[INIT] Candidates loaded: {len(results)}")

        deleted = 0

        for row in results:
            
            candidate_string=row[0]
            candidate_ngram=row[1]
            candidate_frequency=row[2]
            candidate_terms_one_more=candidate_ngram +1 #cerco candidati che hanno una parola in più rispetto ad A- es row[2]= machine learning n+1=3 machine learning model
            fmax= candidate_frequency*percent/100 + candidate_frequency #considero simili tutte le frequenze dentro questo intervallo
            fmin= candidate_frequency*percent/100 - candidate_frequency

            if verbose:
                print("\n---")
                print(f"[A] {candidate_string}")
                print(f"n={candidate_ngram}, freq={candidate_frequency}")
                print(f"target n+1={candidate_terms_one_more}")
                print(f"freq range: [{fmin}, {fmax}]")
            
            self.sqlmanager.cur.execute("SELECT candidate,frequency FROM term_candidates where frequency <="+str(fmax)+" and frequency>="+str(fmin)+"  and n ="+str(candidate_terms_one_more)) #Cerca candidati: con lunghezza n+1, con frequenza simile a fa
            results2=self.sqlmanager.cur.fetchall()

            if verbose:
                print(f"[B] matches found: {len(results2)}")

            for filtered_candidate in results2:
                filtered_candidate_string=filtered_candidate[0]
                if verbose:
                    print(f"compare: {filtered_candidate_string}")

                if candidate_string != filtered_candidate_string and candidate_string in filtered_candidate_string:
                    if verbose:
                        print(f"delete: {candidate_string}")
                    self.sqlmanager.delete_candidate_with_condition(candidate_string)
                    deleted +=1
                    break

        if verbose:
            print(f"\ntotal deleted: {deleted}")



    
    def case_normalization(self,verbose=False):
        results=self.sqlmanager.get_from_candidate_terms(columns=["candidate", "frequency"], order_by="frequency DESC") #che ora ovviamente miglioreremo-cioè metteremo nel sqlite manager
        
        #ora metto tutto in un dizionario per salvare le frequenze
        
        freq_dict = {}

        for term, freq in results:
            key = term.lower()
            
            if key in freq_dict:
                freq_dict[key] += freq
            else:
                freq_dict[key] = freq

        self.sqlmanager.delete_term_candidates()

        data = []
        for term, freq in freq_dict.items(): #iteriamo su ogni coppia del dizionario
            n = len(term.split()) #conto quante parole ha l'n gramma
            data.append((term, n, freq, "freq", freq))



        self.sqlmanager.insert_candidate_terms(data)

#serve per sommare le frequenze dei termini che erano diversi prima della case normalization
    def merge_term_frequencies(self, verbose=False):
        results = self.sqlmanager.get_from_candidate_terms(columns=["candidate", "frequency"])

        freq_dict = {}

        for item in results:

            term, freq = item #unpacks the tuple (candidate, freq)- now we have to variable- a string and an integer
            key = term.strip()

            freq_dict[key] = freq_dict.get(key, 0) + freq #merging frequencies


        self.sqlmanager.delete_term_candidates()

        data = [
            (term, len(term.split()), freq, "freq", freq)
            for term, freq in freq_dict.items()
        ]

        self.sqlmanager.insert_candidate_terms(data)





    
    

