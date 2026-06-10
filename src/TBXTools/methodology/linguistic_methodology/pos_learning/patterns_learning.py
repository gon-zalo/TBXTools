
import operator

class PatternsLearning:
    '''
    Manages automatic learning of POS patterns to perform linguistic extraction
    '''
    def __init__(self): 
        pass
         
    #almost the same as the old code- it works but you'll have to make it more pythonic
    def learn_linguistic_patterns(self,outputfile, evaluation_terms,filtered_tagged_ngrams, showfrequencies=False, encoding="utf-8",verbose=True,representativity=100):
        learntpatterns={}
        sortida = open(outputfile, "w", encoding=encoding)
        acufreq=0 

        print(f"[DEBUG] Found {len(evaluation_terms)} evaluation terms in DB.")

        # for evaluation_term in evaluation_terms:
            # results = self._sqlite.get_tagged_ngrams(ngram_filter=evaluation_term[0])

        results = filtered_tagged_ngrams
        # aplanar la lista / flatten list
        if len(results)>0: 
            for a in results:
                if a:
                    ng = a[0][0]
                    n = a[0][1]
                    frequency = a[0][2]
                    # ng=a[0]
                    
                    nglist=ng.split()
                    # n=a[1]
                    # frequency=a[2]

                    candidate=[]
                    ngtokenstag=ng.split()
                    for ngt in ngtokenstag:
                        candidate.append(ngt.split("|")[0])
                    candidate=" ".join(candidate)

                    t2=ng.split()
                    t1=candidate.split()
                    patternbrut=[]

                    for position in range(0,n):
                        t2f=t2[position].split("|")[0]
                        t2l=t2[position].split("|")[1]
                        t2t=t2[position].split("|")[2]
                        patternpart=""
                        if t1[position]==t2l:
                            patternpart="|#|"+t2t
                        elif t1[position]==t2f:
                            patternpart="#||"+t2t
                        patternbrut.append(patternpart)

                    pattern=" ".join(patternbrut)

                    if pattern in learntpatterns:
                        learntpatterns[pattern]+=n
                        acufreq+=n
                    else:
                        learntpatterns[pattern]=n
                        acufreq+=n

        sorted_x = sorted(learntpatterns.items(), key=operator.itemgetter(1),reverse=True)
        results=[]
        acufreq2=0
        
        for s in sorted_x:
            percent=100*acufreq2/acufreq
            if percent>representativity:
                break
            acufreq2+=s[1]
            if showfrequencies:
                cadena=str(s[1])+"\t"+s[0]
            else:
                cadena=s[0]
            sortida.write(cadena+"\n")
            if verbose:
                print(cadena)
        
        sortida.close()
    
        return learntpatterns
                                

    
