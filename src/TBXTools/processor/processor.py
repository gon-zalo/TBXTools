from nltk.tokenize import RegexpTokenizer
from ..methodology.linguistic.tagger import LinguisticTagger
from ..utils.utils import get_model_from_code
import nltk
from nltk.util import ngrams as compute_ngrams
import re 

class Processor:

    '''Manages the text preprocessing pipeline for terminology extraction. This class provides methods for tokenizing text segments, applying case and nest normalizations, and filtering candidate terms using stopwords and regular expressions.

    Attributes:
        stopwords (list/set): A collection of standard words to filter out.
        inner_stopwords (list/set): A collection of words to filter out when found inside a term.   
    '''

    def __init__(self):

        self.stopwords = None
        self.inner_stopwords = None
        self.nmin = None
        self.nmax = None
        self._lang_code = None
        self.chosen_spacy_model = get_model_from_code(self._lang_code)
        self._tagger = LinguisticTagger(self.chosen_spacy_model)
    
    def apply_case_normalization(self, candidate_terms, verbose=False): 
        '''
        Performs case normalization. If a capitalized term exists as non-capitalized, the capitalized one will be deleted and the frequency of the non-capitalized one will be increased by the frequency of the capitalized.

        Args:
          candidate_terms: a list of tuple containing the candidate terms 
          verbose: If True, enables detailed logging. Defaults to False.
        
        Returns:
          normalized_terms: A new list of tuple after applying case normalization.
        '''
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
    
    def nest_normalization(self, candidate_terms, percent=10, verbose=False):
        """
        Normalizes candidate term frequencies by accounting for nested subterms. Reduces the frequency of terms that appear inside longer candidate terms. A frequency compatibility interval (±percent%) is defined around each candidate term's frequency. The frequency of a nested term is only subtracted from the base term if it falls within this interval. Terms whose normalized frequency drops to 0 are removed from the final list.

        Args:
          candidate_terms: a list of tuple containing the candidate terms 
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
            candidate_term_freq = row[2]

            if candidate_term_n not in terms_by_n:
                terms_by_n[candidate_term_n] = []

            terms_by_n[candidate_term_n].append((candidate_term, candidate_term_freq))
   
        for row in candidate_terms:
            candidate_term = row[0]
            candidate_term_n = row[1]
            candidate_term_freq = row[2]

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
       
            updated_row = (candidate_term, candidate_term_n, normalized_freq, "frequency", normalized_freq)

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
          candidates_to_exclude: a list of candidate terms to exclude

        '''

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
        Tokenizes a text segment into word tokens, removing punctuation outside words while preserving internal characters such as apostrophes and hyphens.

        Args: 
          segment (str): A text segment to be tokenized.

        Returns: 
          list[str]: A list of tokens extracted from the segment.
        """
        
        tokenizer = RegexpTokenizer(r"\b\w(?:[\w'‘’.,-]*\w)?\b")
        token = tokenizer.tokenize(segment)

        return token
    
    def filter_by_stopwords(self, term):
        """
        Filters a candidate term by checking for invalid stopwords. A term is rejected (returns None) if it contains a standard stopword at its boundaries (start/end) or an inner stopword in its middle tokens.

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
        print("Starting POS tagging")
                
        tagged_segments = []
        for segment in segments:

            single_tagged_segment = self._tagger.tag_segment(segment)

            if single_tagged_segment:
                tagged_segments.append((single_tagged_segment,))

        return tagged_segments
    

    def ngrams_calculation(self, segments, corpus_is_tagged= False, minfreq=2):
        
        ngramsFD = nltk.probability.FreqDist()
        nmin = self.nmin
        nmax = self.nmax

        for segment in segments:
            if corpus_is_tagged:
                tokens = segment[0].split()
            else:
                tokens = self.tokenize(segment)
            
            for n in range(nmin, nmax + 1):  
                ngrams_list = compute_ngrams(tokens, n) 
                for ngram in ngrams_list:
                    ngramsFD[ngram] += 1
        
        ngrams_output = []
        for ngram, freq in ngramsFD.most_common(): 
            if freq >= minfreq:
                if corpus_is_tagged:
                    candidate_words = [ngt.split("|")[0] for ngt in ngram]
                    #parte incriminata
                    clean_ngram = " ".join(candidate_words)
                    ngram_row = (clean_ngram, " ".join(ngram), len(ngram), freq)
                else:
                    ngram_row = (" ".join(ngram), len(ngram), freq) 
                
                ngrams_output.append(ngram_row)
            
        return ngrams_output
    

    
    
    
  

