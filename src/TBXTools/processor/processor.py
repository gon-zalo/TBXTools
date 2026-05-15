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
        

    
    def nest_normalization(self, candidate_terms, percent=10, verbose=False):
        '''
        Removes candidate terms that are nested inside another term with similar frequency.
        '''
        print("Applying nest normalization")
        terms_to_delete = []
        terms_by_n = {}

        for row in candidate_terms:
            candidate_term = row[0]
            candidate_term_n = row[1]
            candidate_term_freq = row[2]

            if candidate_term_n not in terms_by_n:
                terms_by_n[candidate_term_n] = []

            terms_by_n[candidate_term_n].append((candidate_term, candidate_term_freq))

        for row in candidate_terms:

            candidate_term = row[0]
            candidate_term_n = row[1]
            candidate_term_freq = row[2]

            second_term_n = candidate_term_n + 1

            if second_term_n not in terms_by_n:
                continue

            fmax = candidate_term_freq * percent/100 + candidate_term_freq
            fmin = candidate_term_freq * percent/100 - candidate_term_freq

            for filtered_term, filtered_term_freq in terms_by_n[second_term_n]:

                if filtered_term_freq < fmin or filtered_term_freq > fmax:
                    continue

                if candidate_term != filtered_term and candidate_term in filtered_term:

                    terms_to_delete.append(candidate_term)

                    if verbose:
                        print(candidate_term_freq,candidate_term,"-->",filtered_term_freq,filtered_term)

        return terms_to_delete

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
                


    
    #it works
    def tokenize(self, segment):
        tokenizer= RegexpTokenizer(r"\b\w(?:[\w'.,-]*\w)?\b")
        token = tokenizer.tokenize(segment)
        return token
    
    


