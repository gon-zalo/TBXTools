class Results:
    '''
    Manages results returned by the different methodologies.

    Attributes:
        _terms: A list of extracted terms.
        _ngrams: A list of extracted Ngrams.
        _tokens: A list of extracted tokens.
        _tagged_ngrams: A list of tagged extracted Ngrams.
        _methodology: Class to manage the methodology object.
        _sqlite: Class to manage the SQLite database.
    '''
    def __init__(self, *, terms=None, ngrams=None, tagged_ngrams=None, tokens=None, linguistic_patterns=None):
        self._terms = terms or []
        self._ngrams = ngrams or []
        self._tagged_ngrams= tagged_ngrams or []
        self._linguistic_patterns = linguistic_patterns or []
        self._tokens = tokens or []

        self._methodology = None
        self._sqlite = None

    # [0] is the first element in the tuple (table row)
    def terms(self, limit=20):
        '''Gets the list of terms

        Args:
            limit: The number of terms accessed. Default is 20.

        Return:
            list: a list of terms.        
        '''
        terms = [term[0] for term in self._terms]

        if limit == None:
            return terms
        
        return terms[:limit]

    def tokens(self, limit=20):
        '''Gets the list of tokens

        Args:
            limit: The number of terms accessed. Default is 20.

        Return:
            list: a list of tokens.        
        '''
        tokens = [token[0] for token in self._tokens]

        if limit == None:
            return tokens
        
        return tokens[:limit]
    
    def ngrams(self, limit=20): 
        '''Gets the list of Ngrams

        Args:
            limit: The number of Ngrams accessed. Default is 20.

        Return:
            list: a list of Ngrams.        
        '''
        ngrams = [ngram[0] for ngram in self._ngrams]

        if limit == None:
            return ngrams
        
        return ngrams[:limit]
    
    def tagged_ngrams(self, limit=20): 
        '''Gets the list of Tagged Ngrams
        
        Args:
            limit: The number of Tagged Ngrams accessed. Default is 20.
            
        Return:
            list: a list of Tagged Ngrams.
        '''
        tagged_ngrams= [tagged_ngram[0] for tagged_ngram in self._tagged_ngrams]

        if limit == None:
            return tagged_ngrams

        return tagged_ngrams[:limit]
    
    def nest_normalization(self, percent=10, verbose=False):
        '''Performs nest normalization of the terms.

        Args:
            percent: The frequency compatibility interval that is used to calculate if a term is nested inside another.
            verbose (bool): Print the process in the console. 
        '''
        candidate_terms = self._terms

        filtered_terms = self._methodology.processor.nest_normalization(candidate_terms=candidate_terms, percent=percent, verbose=verbose)

        self._sqlite.delete_candidate_terms()
        self._sqlite.insert_candidate_terms(filtered_terms)
        self._terms = filtered_terms
  
    def tsr(self, tsr_terms=None, type=None, max_iterations=10000000000, verbose=True):

        print("Applying TSR filter")

        tsr_terms = self._sqlite.load_tsr_terms(tsr_terms=tsr_terms)
    
        if tsr_terms is None:
            tsr_terms = self._sqlite.get_tsr_terms()

        if not tsr_terms:
            print("TSR terms not found. Not applying TSR filter")
            return

        candidate_terms = self._terms
        filtered_terms = self._methodology.processor.apply_tsr_filter(tsr_terms=tsr_terms, candidate_terms=candidate_terms, type=type, max_iterations= max_iterations, verbose=verbose)
        
        self._terms = filtered_terms
        self._sqlite.delete_candidate_terms() 
        self._sqlite.insert_candidate_terms(self._terms)
        print(f"TSR filter completed. {len(self._terms)} candidates saved.")
            
    def regex_exclusion(self, regexes=None, verbose=False):
        '''
        Deletes term candidates matching a set of regular expresions loaded in the Extractor() class.
        '''
        print("Applying regex exclusion")
       
        regexes = self._sqlite.load_exclusion_regexes(exclusion_regexes=regexes)

        if regexes is None:
            regexes = self._sqlite.get_exclusion_regexes()

        if not regexes:
            print("Exclusion regexes not found. Not applying regex exclusion.")
            return

        else:
            candidate_terms = self._sqlite.get_candidate_terms()

            candidates_to_exclude = self._methodology.processor.regex_exclusion(regexes=regexes, candidate_terms=candidate_terms, verbose=verbose)

            if candidates_to_exclude:
                self._sqlite.delete_specific_candidate_term(candidates=candidates_to_exclude)
                print(f"Excluded {len(candidates_to_exclude)} terms")
            else:
                print("No candidate terms excluded")

    def save_candidates(self, path):
        '''
        Save the candidate terms to disk. The file is saved in the specified format. If no format is provided, it defaults to .txt.

        Supported formats: .txt, .csv, .xlsx

        Args:
            path: Path of the file to be saved.
        '''
        from pathlib import Path
        import pandas as pd

        path = Path(path)
        extension = path.suffix.lower()
        candidate_terms = self._terms
        output = pd.DataFrame(candidate_terms, columns=['candidate', 'n', 'measure', 'value'], index=None)

        if not extension:
            extension = ".txt"
            path = path.with_suffix(extension)

        if extension == ".txt":
            output.to_csv(path, index=False, sep="\t")

        elif extension == ".csv":
            output.to_csv(path, index=False)
            
        elif extension == ".xlsx":
            output.to_excel(path, index=False)

        else:
            raise ValueError(f"Unsupported format '{extension}'. Supported formats: .txt, .csv, .xlsx")