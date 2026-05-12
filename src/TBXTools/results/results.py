from ..processor import Processor
from ..sqlite import SQLite
import sys

class Results:

    def __init__(self, *, terms=None, ngrams=None, tokens=None, extractor_info=None):
        self._terms = terms or []
        self._ngrams = ngrams or []
        self._tokens = tokens or []
        self._extractor_info = extractor_info or None
        self._processor = Processor()
        self._sqlite = None

# ACCESSING ATTRIBUTES
    # [0] is the first element in the tuple (table row)
    def terms(self, limit=20):
        terms = [term[0] for term in self._terms]
        return terms[:limit]

    def tokens(self, limit=20):
        tokens = [token[0] for token in self._tokens]
        return tokens[:limit]
    
    def ngrams(self, limit=20):
        ngrams = [ngram[0] for ngram in self._ngrams]
        return ngrams[:limit]
    
    def nest_normalization(self, percent=10, verbose=False):

        if self._extractor_info != "statistical":
            print(f"Error: Nest normalization cannot be run with {self._extractor_info} extractor")
            sys.exit()

        else:
            candidate_terms = self._terms

            filtered_terms = []
            normalized_terms = self._processor.nest_normalization(candidate_terms=candidate_terms, percent=percent, verbose=verbose)

            filtered_terms = [row for row in candidate_terms if row[0] not in normalized_terms]

            self._sqlite.delete_candidate_terms()
            self._sqlite.insert_candidate_terms(filtered_terms)
            self._terms = filtered_terms

    # does not fully work, more info in: processor.regex_exclusion()
    def regex_exclusion(self, verbose=False):
        print("Applying regex exclusion")
        regexes = self._sqlite.get_exclusion_regexes()
        candidate_terms = self._sqlite.get_candidate_terms()

        candidates_to_exclude = self._processor.regex_exclusion(regexes=regexes, candidate_terms=candidate_terms)

        if candidates_to_exclude:
            for candidate in candidates_to_exclude:
                self._sqlite.delete_specific_candidate_term(candidate=candidate)
                print(f"Excluded {len(candidates_to_exclude)} terms")
        else:
            print("No candidate terms excluded")

    def save_candidates(self, file_name): # save as csv?
        candidate_terms = self._sqlite.get_candidate_terms()
        with open(file_name, "w", encoding='utf-8') as f:
            for row in candidate_terms:
                f.write(",".join(str(element) for element in row) + "\n")