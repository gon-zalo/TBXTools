from .._utils.utils import get_spacy_model_from_code

class Processor:

    '''Manages the text preprocessing pipeline for terminology extraction. This class
    provides methods for tokenizing text segments, applying lemmatization, case and nest normalizations, and filtering candidate terms using stopwords and regular expressions.

    Attributes:
        stopwords (list/set): A collection of standard words to filter out.
        inner_stopwords (list/set): A collection of words to filter out when found inside a term.
        nmin (int): The minimum number of words a candidate term can contain.
        nmax (int): The maximum number of words a candidate term can contain.
        lang_code (str): The ISO code for the language.
        model_name (str): The name of the spacy model used (e.g., "en_core_web_sm" or "ca_core_news_sm").
        nlp: The NLP pipeline or model used for text processing.
        
        
    '''

    def __init__(self):
        self.stopwords = None
        self.inner_stopwords = None
        self.nmin = None
        self.nmax = None
        self.lang_code = None
        self.model_name = None
        self.nlp = None

    
    def case_normalization(self, candidate_terms, verbose=False): 
        '''
        Performs case normalization. If a capitalized term exists as non-capitalized, the capitalized one will be deleted and the frequency of the non-capitalized one will be increased by the frequency of the capitalized.

        Args:
          candidate_terms: a list of tuple containing the candidate terms. 
          verbose: If True, enables detailed logging. Defaults to False.
        
        Returns:
          normalized_terms: A new list of tuple after applying case normalization.
        '''
        print("Applying case normalization")

        freq_dict = {}

        for terms_row in candidate_terms:
            term = terms_row[0]
            freq = terms_row[3]

            key = term.lower().strip()
            freq_dict[key] = freq_dict.get(key, 0) + freq

        normalized_terms = []
        for term, freq in freq_dict.items():
            n = len(term.split())

            row = (term, n, "frequency", freq)
            normalized_terms.append(row)

            if verbose:
                print(term, "->", freq)

        return normalized_terms
    
    def lemmatization(self, candidate_terms, verbose=False):
        '''
        Performs lemmatization. Applies lemmatization to all candidate terms and merges duplicates by summing their frequencies.

        Args:
          candidate_terms: a list of tuple containing the candidate terms. 
          verbose: If True, enables detailed logging. Defaults to False.
        
        Returns:
          normalized_terms: A new list of tuple after applying lemmatization.
        '''
        
        from spacy.tokens import Doc 

        from .._utils.utils import load_spacy_model
        
        if self.lang_code is not None and self.model_name is None:
            self.model_name = get_spacy_model_from_code(self.lang_code)


        if self.nlp is None: 
            if self.model_name is None:
                raise ValueError( #maybe we can eliminate this error- we will always set a lang code in the extraction
                    "Unable to start lemmatization: the language (lang_code) has not been set"
                )
            
            self.nlp = load_spacy_model(self.model_name)
            
        print("Applying lemmatization")
        freq_dict = {}

        for terms_row in candidate_terms:
            term = terms_row[0].strip()
            freq = terms_row[3]

            words = term.split()

            doc = Doc(self.nlp.vocab, words=words)

            for name, proc in self.nlp.pipeline:
                doc = proc(doc)

            lemmatized_term = " ".join([token.lemma_.strip() for token in doc])

            freq_dict[lemmatized_term] = freq_dict.get(lemmatized_term, 0) + freq

        normalized_terms = []
        for lemma, freq in freq_dict.items():
            n = len(lemma.split())

            row = (lemma, n, "frequency", freq)
            normalized_terms.append(row)

            if verbose:
                print(f"{lemma} -> {freq}")

        return normalized_terms
        
    
    def nest_normalization(self, candidate_terms, percent=10, verbose=False):
        """
        Normalizes candidate term frequencies by accounting for nested subterms. Reduces the frequency of terms that appear inside longer candidate terms. A frequency compatibility interval (±percent%) is defined around each candidate term's frequency. The frequency of a nested term is only subtracted from the base term if it falls within this interval. Terms whose normalized frequency drops to 0 are removed from the final list.

        Args:
          candidate_terms: a list of tuple containing the candidate terms.
          percent (int or float, optional): The percentage threshold defining the compatibility interval around each frequency. Defaults to 10.
          verbose: If True, enables detailed logging. Defaults to False.
        
        Returns:
          updated_terms: A new list of tuple after applying nest normalization.


        """
        print("Applying nested frequency normalization")

        updated_terms = []
        terms_by_n = {}

        for row in candidate_terms:
            candidate_term = row[0]
            candidate_term_n = row[1]
            candidate_term_freq = row[3]
            if candidate_term_n not in terms_by_n:
                terms_by_n[candidate_term_n] = []

            terms_by_n[candidate_term_n].append((candidate_term, candidate_term_freq))
   
        for row in candidate_terms:
            candidate_term = row[0]
            candidate_term_n = row[1]
            candidate_term_freq = row[3]

            nested_frequency = 0

            # frequency bounds (POST control)
            fmax = candidate_term_freq + candidate_term_freq * percent / 100
            fmin = candidate_term_freq - candidate_term_freq * percent / 100
            
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
                                if fmin <= longer_term_freq <= fmax:
                                    nested_frequency += longer_term_freq 
                                    break
                            
            # compute the normalized frequency
            normalized_freq = max(candidate_term_freq - nested_frequency, 0)
       
            updated_row = (candidate_term, candidate_term_n, "frequency", normalized_freq)

            # remove terms whose normalized frequency becomes 0
            if normalized_freq > 0:
                updated_terms.append(updated_row)

            elif verbose:
                print(
                f"Removed '{candidate_term}' "
                f"because normalized frequency became 0"
                )
    
        return updated_terms
    
    def regex_exclusion(self, regexes, candidate_terms, verbose=False):
        '''
        Remove candidate terms that match regex expressions. It takes data in tuples as rows and outputs a list of candidate terms to exclude.

        Args:
          regexes: regular expression patterns used to match and filter out unwanted terms.
          candidate_terms: a list of tuple containing the candidate terms.
          verbose: If True, enables detailed logging. Defaults to False.
        
        Returns:
          candidates_to_exclude: a list of candidate terms to exclude.

        '''
        import re
         
        candidates_to_exclude = []
        for candidate_row in candidate_terms:
            candidate = candidate_row[0]
            candidate_n = candidate_row[1]
            candidate_n = int(candidate_n)

            for regex in regexes:
                regex = regex[0]
                regex_n = len(regex.split())
                match = re.fullmatch(regex, candidate)

                if match and regex_n == candidate_n:
                    candidates_to_exclude.append(candidate)

                    if verbose:
                        print(f"'{candidate}' removed by: {regex}")

        return candidates_to_exclude
             
    def tokenize(self, segment):
        """
        Tokenizes a text segment into word tokens using a custom regular expression.

        This tokenizer strips away general boundary punctuation, but keeps optional surrounding parentheses attached to the tokens. It also preserves internal 
        word characters such as apostrophes, hyphens, periods, commas, and the 
        Catalan middle dot (·).

        Args: 
          segment (str): A text segment to be tokenized.

        Returns: 
          list[str]: A list of tokens extracted from the segment.
        """
        from nltk.tokenize import RegexpTokenizer
        #tokenizer = RegexpTokenizer(r"\b\w(?:[\w'‘’.,-]*\w)?\b")
        tokenizer = RegexpTokenizer(r"\(?\b\w(?:[\w'‘’.,-·]*\w)?\b\)?")
        token = tokenizer.tokenize(segment)
        
        return token
    
    def filter_by_stopwords(self, term):
        """
        Filters a candidate term by checking for invalid stopwords. A term is rejected(returns None) if it contains a standard stopword at its boundaries (start/end) or an inner stopword in its middle tokens.

        Args: 
          term(str): The candidate term string to validate.
        
        Returns:
          str or None: The original term string if it passes all stopword filters, otherwise None.
        """
        split_term = term.lower().split()

    #stopwords at boundaries
    
        if (split_term[0] in self.stopwords or split_term[-1] in self.stopwords):
            return None

    # inner stopwords
        for token in split_term[1:-1]:
            if token in self.inner_stopwords:
                return None

        return term
    
    def filter_by_stopwords_linguistic(self, term):
        """
        Filters a candidate term (in this case a tagged ngram) by checking for invalid stopwords. A term is rejected (returns None) if it contains a standard
        stopword at its boundaries (start/end).

        Args: 
          term(str): The candidate term string to validate.
        
        Returns:
          str or None: The original term string if it passes all stopword filters, otherwise None.
        """
        split_term = term.lower().split()
        
        first_word = split_term[0].split("|")[1]
        if first_word in self.stopwords:
            return None
        
        last_word = split_term[-1].split("|")[1]
        if last_word in self.stopwords:
            return None
        
        return term
    
    # linguistic processing
    def translate_pattern(self, linguistic_patterns):
        """
        Translates a list of linguistic patterns into valid regular expressions.

        This method processes each pattern string (or the first element of a tuple), tokenizes it by whitespace, and converts specific custom syntax elements into regex equivalents.

        Args:
           linguistic_patterns (list of str or list of tuple): A list containing the linguistic patterns to be translated. If an element is a tuple, only the first string item is processed.

        Returns:
           list of str: A list of compiled regular expression strings."""

        translated_patterns= []
        
        for pattern_str in linguistic_patterns:
            if isinstance(pattern_str, tuple):
                pattern_str = pattern_str[0]

            aux = []
            for ptoken in pattern_str.split():
                auxtoken = []
                ptoken = ptoken.replace(".*", "[^\s]+") 
                for pelement in ptoken.split("|"):
                    if pelement == "#":
                        auxtoken.append("([^\s]+?)")                    
                    elif pelement == "":
                        auxtoken.append("[^\s]+?")
                    else:
                        if pelement.startswith("#"):
                            auxtoken.append("(" + pelement.replace("#", "") + ")")
                        else:
                            auxtoken.append(pelement)
                aux.append("\|".join(auxtoken))
            tp = "(" + " ".join(aux) + ")"
            
            translated_patterns.append(tp)
            
        return translated_patterns
    
    def create_tagged_segments(self, segments):
        """
        Pos tags a list of text segments.

        Args:
          segment (list of str): The input text string to be processed.

        Returns:
          tagged_segments (list of str): A list of POS tagged segments.
        """
        from .._utils.utils import load_spacy_model

        if self.lang_code is not None and self.model_name is None:
            self.model_name = get_spacy_model_from_code(self.lang_code)

        if self.nlp is None:
            if self.model_name is None:
                raise ValueError(
                    "Unable to start POS tagging: the language (lang_code) has not been set"
                )
            self.nlp = load_spacy_model(self.model_name)

        from ..methodology.linguistic.tagger import LinguisticTagger

        tagger = LinguisticTagger(self.nlp)

        tagged_segments = []
        for segment in segments:

            single_tagged_segment = tagger.tag_segment(segment)

            if single_tagged_segment:
                tagged_segments.append(single_tagged_segment)

        return tagged_segments
    
    def ngram_calculation(self, segments, is_corpus_tagged=False, minfreq=2):
        '''
        Calculates ngrmas and their frequencies from a list of text segments.

        If the corpus is tagged, it extracts both the raw text ngrams and the tagged ngrams to use when applying the linguistic extraction.

        Args:
          segments (list) : A list of text segments to process.
          is_corpus_tagged (bool) : If True the corpus is tagged. If False the corpus is not tagged. Defaults to False
          min_freq(int) : The minimum frequency threshold. Only ngrams appearing at least "minfreq" times will be included in the output.

        Returns:
          ngrams_output (list of tuple) : A list of tuples containing the ngram strings with their lenght and frequency.
          tagged_ngrams_output (list of tuple) : A list of tuples containing the original tagged n-grams with their length and frequency. This list remains empty if `is_corpus_tagged` is False.       
        '''
        import nltk
        from nltk.util import ngrams as compute_ngrams
        
        ngramsFD = nltk.probability.FreqDist()
        nmin = self.nmin
        nmax = self.nmax
        for segment in segments:
            if is_corpus_tagged:
                tokens = segment.split()
            else:
                tokens = self.tokenize(segment)

            for n in range(nmin, nmax + 1):  
                ngrams_list = compute_ngrams(tokens, n) 
                for ngram in ngrams_list:
                    ngramsFD[ngram] += 1

        ngrams_output = []
        tagged_ngrams_output = []
        for ngram, freq in ngramsFD.most_common(): 
            if freq >= minfreq:
                if is_corpus_tagged:
                    candidate_words = [ngt.split("|")[0] for ngt in ngram]
                    clean_ngram = " ".join(candidate_words)

                    ngrams_output.append((clean_ngram, len(ngram), freq))
                    tagged_ngrams_output.append((" ".join(ngram), len(ngram), freq))

                else:
                    ngrams_output.append((" ".join(ngram), len(ngram), freq))

        return ngrams_output, tagged_ngrams_output
    
    def apply_tsr_filter(self, tsr_terms, candidate_terms, type="strict", max_iterations=10000000000, verbose=False): 
        '''
        Filters the extracted candidate terms using the TSR (Token Slot Recognition) method. The algorithm is based on the concept of terminological token to filter out term candidates. It reads the terminological tokens from a list of terms (tsr_terms) and stores them taking into account their position in the terminological unit (first, middle, last). The TSR method filters term candidates by taking into account their tokens. To do so, 3 filtering variants are designed: strict, flexible and combined. 
        In strict TSR filtering, a term candidate will be kept only if all the tokens are present in the corresponding position. In flexible TSR filtering, a term candidate will be kept if any of the tokens is present in the corresponding position. In combined TSR filtering, strict filtering is first used and is then followed by flexible filtering. In flexible and combined mode the algorithm performs the filtering process recursively, that is, by enlarging the list of terminological tokens with the new selected term candidates.

        Args:
            tsr_terms: The reference standard terms.
            candidate_terms (list of list): Candidates terms.
            type (str, optional): Filtering mode ("strict", "flexible", "combined"). Defaults to "combined".
            max_iterations (int, optional): Loop ceiling for recursion. Defaults to 10000000000.
            verbose (bool, optional): Defaults to False.

        Returns:
            updated_terms(list of list): Final candidate terms that passed the tsr filter structured as [term, n, freq, measure, value].
        '''
        component = {}  
        firstcomponent = {}
        middlecomponent = {}
        lastcomponent = {}
        
        #from tsr terms list to the 4 dictionaries
        for tsr_term in tsr_terms:
            tsr_ngrams = tsr_term.split() 
            if len(tsr_ngrams)==1: #UNIGRAMS
                firstcomponent[tsr_ngrams[0].lower()] = 1 
                lastcomponent[tsr_ngrams[0].lower()] = 1
            if len(tsr_ngrams)>= 2: 
                firstcomponent[tsr_ngrams[0].lower()] = 1
                lastcomponent[tsr_ngrams[-1].lower()] = 1
                component[tsr_ngrams[0].lower()]=1
                component[tsr_ngrams[-1].lower()]=1
                if len(tsr_ngrams)>=3:
                    for i in range(1,len(tsr_ngrams)-1):
                        middlecomponent[tsr_ngrams[i].lower()]=1
                        component[tsr_ngrams[i].lower()]=1

        new=True  #flag used to control the loop- initialized True to ensure the loop runs at least once
        newcandidates={} #candidate-frequency
        hashmeasure={} #to store the measurement types for each accepted candidate ("tsr")
        #hashvalue={} #stores the values for each accepted candidate
        
        iterations=0 #how many times the loop executes
        while new: #the loop keeps running as long as new is True
            iterations+=1
            if verbose: print("ITERATION",iterations)
            new=False #Immediately resets the new flag to False at the beginning of the round. If the code later finds and accepts a new candidate term, it will set this back to True to trigger another iteration. If no new terms are found, the loop will exit.
            #value=max_iterations-iterations 
            
            for term in candidate_terms:
                candidate=term[0]
                n=term[1]
                frequency=term[3]
                measure="frequency" 
                
                #Setting Up Validation Flags for the Current Candidate
                first_c=False #It will be switched to True if the first word of the candidate matches the valid component criteria
                middle_c=False
                last_c=False
                rcamps=candidate.split()
                truesfalses=[] #initializes an empty list designed to collect the individual boolean verdicts (e.g., [True, False]) for each word of the candidate during the upcoming validation checks
                
                first_n = str(rcamps[0]).lower()
                last_n = str(rcamps[-1]).lower()
                
                if first_n in firstcomponent: 
                    first_c=True
                    truesfalses.append(True)
                else:
                    truesfalses.append(False)
                
                if last_n in lastcomponent: 
                    last_c=True
                    truesfalses.append(True)
                else:
                    truesfalses.append(False)

                if n>2:
                    middle_c=True
                    for i in range(1,n-1):
                        mid_n = str(rcamps[i]).lower()
                        if not mid_n in middlecomponent: 
                            middle_c=False
                    if middle_c==True:
                        truesfalses.append(True)
                    else:
                        truesfalses.append(False)

                if type=="strict":
                        if not False in truesfalses:
                            if not candidate in newcandidates: 
                                newcandidates[candidate]=frequency
                                hashmeasure[candidate]=measure
                                #hashvalue[candidate]=value
                                new=True #Because a brand-new valid term was discovered during this round, the new flag is flipped back to True.
                                
                                w_first_low, w_last_low = rcamps[0].lower(), rcamps[-1].lower()
                                firstcomponent[w_first_low]=1 
                                lastcomponent[w_last_low]=1

                elif type=="flexible": 
                    if True in truesfalses:
                        if not candidate in newcandidates:
                            newcandidates[candidate]=frequency
                            hashmeasure[candidate]=measure
                            #hashvalue[candidate]=value
                            new=True
                            w_first_low, w_last_low = rcamps[0].lower(), rcamps[-1].lower()
                            firstcomponent[w_first_low]=1
                            lastcomponent[w_last_low]=1
                            component[w_first_low]=1
                            component[w_last_low]=1

                elif type=="combined":
                    if iterations== 1:
                        if not False in truesfalses: 
                            if not candidate in newcandidates:
                                newcandidates[candidate]=frequency
                                hashmeasure[candidate]=measure
                                #hashvalue[candidate]=value     
                                new=True                         
                                w_first_low, w_last_low = rcamps[0].lower(), rcamps[-1].lower()
                                firstcomponent[w_first_low]=1
                                lastcomponent[w_last_low]=1
                                if n>2:
                                    for i in range(1,n-1):
                                        w_mid = rcamps[i].lower()
                                        middlecomponent[w_mid]=1
                                        component[w_mid]=1
                    else:
                        if True in truesfalses:
                            if not candidate in newcandidates:
                                newcandidates[candidate] = frequency
                                hashmeasure[candidate] = measure
                                #hashvalue[candidate] = value
                                new=True
                                
                                w_first_low, w_last_low = rcamps[0].lower(), rcamps[-1].lower()
                                firstcomponent[w_first_low]=1
                                lastcomponent[w_last_low]=1
                                if n>2:
                                    for i in range(1,n-1):
                                        w_mid = rcamps[i].lower()
                                        middlecomponent[w_mid]=1
                                        component[w_mid]=1
                                component[w_first_low]=1
                                component[w_last_low]=1
                                
        updated_terms=[] 
        for new_candidate in newcandidates:
            term= new_candidate
            n=len(new_candidate.split())
            freqtotal=newcandidates[new_candidate]
            measure=hashmeasure[new_candidate]
            #value=hashvalue[new_candidate]
            
            updated_terms.append((term, n, measure, freqtotal))
              
        return updated_terms
