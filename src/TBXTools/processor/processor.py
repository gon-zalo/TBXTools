from nltk.tokenize import RegexpTokenizer
import re


class Processor:

    def __init__(self, stopwords=None, inner_stopwords=None):

        self.stopwords = stopwords 
        self.inner_stopwords = inner_stopwords 
    
    
    #this should work- enseña la comparación entre candidate terms con case_normalization= True y False
    #luego debería estar listo para el pull
    def case_normalization(self, candidate_terms, verbose=False):
        
        print("Applying case normalization")

        freq_dict = {}

    
        for terms_row in candidate_terms:
            term = terms_row[0]
            freq = terms_row[2]

            key = term.lower().strip()
            freq_dict[key] = freq_dict.get(key, 0) + freq

    
        normalized_terms = []

        for term, freq in freq_dict.items():
            n = len(term.split())

            row = (term, n, freq, "freq", freq)
            normalized_terms.append(row)

            if verbose:
                print(term, "->", freq)

        return normalized_terms
    
        #we can maybe add something like the following, to eliminate terms that have frequency= 2 or something like that (since they are a loot)
        #right now it considers candidates that have at least frequency= 2- it comes from the statistical extractor
        # if freq < min_freq: 
                #break
    
    #it works but maybe the code can be shorter
    #he quitado lo de la frecuencia porque por ejemplo por mental health (65) yo quería que me quitara del computo cosas como mental health services que tenía freq= 7
    #pero con fmax = candidate_term_freq * percent/100 + candidate_term_freq
    #fmin = candidate_term_freq * percent/100 - candidate_term_freq
    #y percent= 10
    #La traducción más natural y precisa para el contexto de tu código es:
    #El rango de tolerancia calculado por el código (con el 10%) permite buscar solo términos largos que tengan una frecuencia comprendida entre 58.5 y 71.5.
    #se puede preguntar a patricia si quiere mantener las frecuencias
    def nest_normalization(self, candidate_terms, verbose=False):

        """
    Normalize candidate term frequencies by reducing the frequency
    of terms that occur as nested subterms inside longer candidate terms.

    Terms whose normalized frequency becomes 0 are removed
    from the final candidate list.

    Example:
        mental health -> 10
        community mental health -> 5

    Result:
        mental health -> 5
        community mental health -> 5
    """

        print("Applying nested frequency normalization")

        updated_terms = []
        terms_by_n = {}

        for row in candidate_terms:
            candidate_term = row[0]
            candidate_term_n = row[1]
            candidate_term_freq = row[2]

            if candidate_term_n not in terms_by_n:
                terms_by_n[candidate_term_n] = []

            terms_by_n[candidate_term_n].append(
            (candidate_term, candidate_term_freq)
            )

   
        for row in candidate_terms:
            candidate_term = row[0]
            candidate_term_n = row[1]
            candidate_term_freq = row[2]

            nested_frequency = 0
            
            # compare the current term only with longer terms
            for longer_n, longer_terms in terms_by_n.items():
                if longer_n <= candidate_term_n:
                    continue

                for longer_term, longer_term_freq in longer_terms:

                    if candidate_term == longer_term: #skip identical terms
                        continue

                    #split terms into tokens
                    candidate_tokens = candidate_term.split()
                    longer_tokens = longer_term.split()

                    # search for an exact token sequence match
                    for i in range(len(longer_tokens) - len(candidate_tokens) + 1):
                        window = longer_tokens[i:i + len(candidate_tokens)]

                        if window == candidate_tokens:
                            nested_frequency += longer_term_freq
                            break




            # compute the normalized frequency
            normalized_freq = max(candidate_term_freq - nested_frequency, 0)

        
            updated_row = (
            candidate_term,
            candidate_term_n,
            normalized_freq,
            "frequency",
            normalized_freq
        )
            # remove terms whose normalized frequency becomes 0
            if normalized_freq > 0:
                updated_terms.append(updated_row)

            elif verbose:
                print(
                f"Removed '{candidate_term}' "
                f"because normalized frequency became 0"
                )
    
        return updated_terms
    


    

# NO FUNCIONA CORRECTAMENTE, REVISAR
    def regex_exclusion(self, regexes, candidate_terms, verbose=False):
        '''Deletes term candidates matching a set of regular expresions loaded with the load_sl_exclusion_regexps method.'''
        import re
        
        candidates_to_exclude = []
        for row in regexes:
            regex = row[0]
            regex_n= len(row[0].split())

            compiled_regexes = re.compile(regex)

            for candidate_row in candidate_terms:
                candidate = candidate_row[0]
                candidate_n = candidate_row[1]
                
                match = re.match(compiled_regexes, candidate)
        
                # codigo de prueba con \w+ disorder en el archivo de regexes
                # if match:
                #     print(regex_n, candidate_n)
                #     print(candidate)

                # if regex_n == candidate_n:
                #     if match:
                #         print("true match")
                #         print(match)
                #         print(candidate)
                    # print("match")

                # if match:
                #     if regex_n == candidate_n:
                #         candidates_to_exclude.append(candidate)
                #         print(match)

                if match and regex_n == candidate_n:
                    print("match")
                    candidates_to_exclude.append(candidate)

                    if verbose:
                        print(regex,"-->",candidate)
                    
                    return set(list(candidates_to_exclude))

    def tokenize(self, segment):
        tokenizer = RegexpTokenizer(r"\b\w(?:[\w'‘’.,-]*\w)?\b")
        token = tokenizer.tokenize(segment)

        return token