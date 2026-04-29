class Preprocessor:

    def __init__(self):
        pass
    
    def case_normalization(self, candidate_terms, verbose=False):
        '''
        Performs case normalization. If a capitalized term exists as non-capitalized, the capitalized one will be deleted and the frequency of the non-capitalized one will be increased by the frequency of the capitalized.
        '''
        auxiliar={}

        for terms_row in candidate_terms:
            term = terms_row[0]
            freq = terms_row[2]

            auxiliar[term] = freq

        normalized_terms = []
        for terms_row in candidate_terms:
            # row = []

            term = terms_row[0]
            freq = terms_row[2]
            if not term == term.lower() and term.lower() in auxiliar:

                first_term = term
                second_term = term.lower()

                first_term_freq = freq
                second_term_freq = auxiliar[second_term]

                n = len(second_term.split())

                total_frequency = first_term_freq + second_term_freq

                if verbose:
                    print(first_term, first_term_freq,"-->",second_term, second_term_freq,"-->",total_frequency)

                row = (second_term, n, total_frequency, "freq", total_frequency) # tuples are simpler

                normalized_terms.append(row)

        return normalized_terms

    def regex_exclusion(self, regexes, candidate_terms, verbose=False):
        # NO FUNCIONA CORRECTAMENTE, REVISAR
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
                

    # INTENTO DE IMPLEMENTACIÓN DE NEST NORMALIZATION
    
    # def _get_frequencies(self, candidate_terms, percent=10):
    #     for row in candidate_terms:

    #         print(row)
    #         ta=row[0] # term
    #         fa=row[1] # n
    #         na=row[2] # frequency
    #         nb=na+1

    #         fmax = fa +fa * percent/100
    #         fmin=fa-fa*percent/100

    #         return fmax, fmin, nb


    # def nest_normalization(self, candidate_terms, filtered_candidate_terms, ta, fa, percent=10, verbose=False):
    #     '''
    #     Performs a normalization of nested term candidates. If an n-gram candidate A is contained in a n+1 candidate B and freq(A)==freq(B) or they are close values (determined by the percent parameter, A is deleted B remains as it is)
    #     '''
    #     candidate_terms_to_delete = []
    #     for row in candidate_terms:

    #         candidate_term = row[0]
    #         candidate_term_n = row[1]
    #         candidate_term_freq = row[2]
    #         second_term_n = candidate_term_n + 1

    #         fmax = candidate_term_freq * percent/100 + candidate_term_freq
    #         fmin = candidate_term_freq * percent/100 - candidate_term_freq

    #         # filtered_candidate_terms = self._sqlite.get_filtered_candidate_terms_by_frequency(fmax=fmax, fmin=fmin, nb=second_term_n)

    #         for filtered_row in filtered_candidate_terms:

    #             filtered_term = filtered_row[0]
    #             filtered_term_freq = filtered_row[2]

    #             if not candidate_term == filtered_term and not filtered_term.find(candidate_term)==-1: # que coño es esto

    #                 if verbose:
    #                     print(str(candidate_term_freq),candidate_term,"-->",str(filtered_term_freq),filtered_term)

    #                 candidate_terms_to_delete.append(candidate_term)
        

    #     return candidate_terms_to_delete