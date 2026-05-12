class Processor:

    def __init__(self):
        pass
    
    def case_normalization(self, candidate_terms, verbose=False):
        '''
        Performs case normalization. If a capitalized term exists as non-capitalized, the capitalized one will be deleted and the frequency of the non-capitalized one will be increased by the frequency of the capitalized.
        '''
        print("Applying case normalization")
        auxiliar={}

        for terms_row in candidate_terms:
            term = terms_row[0]
            freq = terms_row[2]

            auxiliar[term] = freq

        normalized_terms = []
        for terms_row in candidate_terms:

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