
from ..processor import Processor
from ..sqlite import SQLite
import sys

class Results:
    '''
    Manages results returned by the different methodologies.

    Attributes:
        _terms: A list of extracted terms.
        _ngrams: A list of extracted Ngrams.
        _tokens: A list of extracted tokens.
        _extractor_info: The name of the methodology used (statistical, linguistic...).
        _processor: Class to process data.
        _sqlite: Class to manage the SQLite database.
    '''
    def __init__(self, *, terms=None, ngrams=None, tokens=None, extractor_info=None):
        self._terms = terms or []
        self._ngrams = ngrams or []
        self._tokens = tokens or []
        self._extractor_info = extractor_info or None

        # passed from Extractor()
        self._processor = None
        self._sqlite = None

# ACCESSING ATTRIBUTES
    # [0] is the first element in the tuple (table row)
    def terms(self, limit=20):
        '''Gets the list of terms

        Args:
            limit: The number of terms accessed. Default is 20.

        Return:
            list: a list of terms.        
        '''
        terms = [term[0] for term in self._terms]
        return terms[:limit]

    def tokens(self, limit=20):
        '''Gets the list of tokens

        Args:
            limit: The number of terms accessed. Default is 20.

        Return:
            list: a list of tokens.        
        '''
        tokens = [token[0] for token in self._tokens]
        return tokens[:limit]
    
    def ngrams(self, limit=20):
        '''Gets the list of Ngrams

        Args:
            limit: The number of Ngrams accessed. Default is 20.

        Return:
            list: a list of Ngrams.        
        '''
        ngrams = [ngram[0] for ngram in self._ngrams]
        return ngrams[:limit]
    
    def nest_normalization(self, percent=10, verbose=False):
        '''Performs nest normalization of the terms.

        Args:
            percent: The frequency compatibility interval that is used to calculate if a term is nested inside another.
            verbose (bool): Print the process in the console. 
        '''
        if self._extractor_info != "statistical":
            print(f"Error: Nest normalization cannot be run with {self._extractor_info} extractor")
            sys.exit()

        else:
            candidate_terms = self._terms

            filtered_terms = self._processor.nest_normalization(candidate_terms=candidate_terms, percent= percent, verbose=verbose)

            self._sqlite.delete_candidate_terms()
            self._sqlite.insert_candidate_terms(filtered_terms)
            self._terms = filtered_terms
            

    def regex_exclusion(self, verbose=False):
        '''
        Deletes term candidates matching a set of regular expresions loaded in the Extractor() class.
        '''
        print("Applying regex exclusion")
        regexes = self._sqlite.get_exclusion_regexes()

        if not regexes:
            print("Exclusion regexes not found. Not applying regex exclusion.")

        else:
            candidate_terms = self._sqlite.get_candidate_terms()

            candidates_to_exclude = self._processor.regex_exclusion(regexes=regexes, candidate_terms=candidate_terms, verbose=verbose)

            if candidates_to_exclude:
                for candidate in candidates_to_exclude:
                    self._sqlite.delete_specific_candidate_term(candidate=candidate)
                print(f"Excluded {len(candidates_to_exclude)} terms")
            else:
                print("No candidate terms excluded")

    def save_candidates(self, file_name):
        '''
        Save the candidate terms to a text file.

        Args:
            file_name: Name of the file to be saved.
        '''
        candidate_terms = self._sqlite.get_candidate_terms()
        with open(file_name, "w", encoding='utf-8') as f:
            for row in candidate_terms:
                f.write(",".join(str(element) for element in row) + "\n")