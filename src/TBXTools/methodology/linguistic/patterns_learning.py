import operator

class PatternsLearning:
    '''
    Manages automatic learning of POS patterns to perform linguistic extraction.
    '''
    def __init__(self): 
        pass
         
    def learn_linguistic_patterns(self,outputfile,filtered_tagged_ngrams, showfrequencies=True, encoding="utf-8",verbose=False,representativity=100):
        '''
        Automatically extracts linguistic patterns from a collection of pre-filtered, POS-tagged n-grams. It sorts the patterns from most to least frequent and writes them to an external text file, using a percentage threshold (representativity) to discard rare patterns.

        Args:

        outputfile (str): The file path where the learned linguistic patterns will be saved.
        filtered_tagged_ngrams (list of tuples): A collection of rows fetched from the database, where each tuple contains (tagged_ngram_string, n_size, frequency).
        showfrequencies (bool, optional): If True, displays the pattern's frequency into the output file. Defaults to True.
        encoding (str, optional): Defaults to "utf-8".
        verbose (bool, optional): Defaults to False.
        representativity (int, optional): A setting (0 to 100) that decides how many patterns to save based on their frequency. It sorts patterns from most to least common and stops saving once your chosen percentage of the total data is reached (setting it to 100 saves everything).

        Returns:
        
        learntpatterns (dict): A dictionary of learned patterns where keys are the generated rule strings (e.g., "|#|NOUN #||ADJ") and values are their corresponding frequencies.
        '''
       
        learntpatterns={} #the key is the pattern and the value is its frequency
        acufreq=0  #to accumulate the frequencies

        results = filtered_tagged_ngrams #('health|health|NOUN professionals|professional|NOUN', 2, 7)- this is filtered tagged ngrams
        if len(results)>0: 
            for tagged_ngram in results:
                if tagged_ngram:
                    tagged_ngram_string = tagged_ngram[0]
                    n = tagged_ngram[1]
                    frequency = tagged_ngram[2]

                    candidate_words=[]
                    ngram_components=tagged_ngram_string.split() #['mental|mental|ADJ', 'disorders|disorder|NOUN']
                    for component in ngram_components:
                        candidate_words.append(component.split("|")[0]) #lista con mental, disorder, ecc...
                    candidate_string=" ".join(candidate_words) #mental disorders

                    tagged_components=tagged_ngram_string.split() #['mental|mental|ADJ', 'disorders|disorder|NOUN']
                    clean_components=candidate_string.split() #['mental', 'disorders']
                    patternbrut=[]

                    for position in range(0,n):
                        clean_text=tagged_components[position].split("|")[0] #mental
                        clean_lemma=tagged_components[position].split("|")[1]
                        clean_tag=tagged_components[position].split("|")[2]
                        patternpart=""
                        if clean_components[position]==clean_lemma: #if mental da ['mental', 'disorders'] == mental
                            patternpart="|#|"+clean_tag
                        elif clean_components[position]==clean_text:
                            patternpart="#||"+clean_tag
                        patternbrut.append(patternpart)

                    pattern=" ".join(patternbrut)

                    if pattern in learntpatterns:
                        learntpatterns[pattern]+=frequency
                        acufreq+=frequency
                    else:
                        learntpatterns[pattern]=frequency
                        acufreq+=frequency

        sorted_patterns = sorted(learntpatterns.items(), key=operator.itemgetter(1),reverse=True) #Sorts the dictionary entries into a list of tuples ordered by their score value in descending order (reverse=True), putting the most prominent patterns at the top
        acufreq2=0
        
        with open(outputfile, "w", encoding=encoding) as sortida:
            for pattern, score in sorted_patterns:
                percent = 100 * acufreq2 / acufreq
                if percent > representativity:
                    break
                acufreq2 += score  
    
                if showfrequencies:
                    cadena = str(score) + "\t" + pattern
                else:
                    cadena = pattern
        
                sortida.write(cadena+"\n")
                if verbose:
                    print(cadena)

        return learntpatterns 
       