from term_extractor import TerminologyExtractor

def main():

    extractor= TerminologyExtractor()
    extractor.create_project("progetto_prova.db")
    extractor.load_corpus("medicina.txt")
    extractor.load_stopwords("stop-eng.txt")
    extractor.load_inner_stopwords("inner-stop-eng.txt")
    extractor.ngram_calculation(nmin=2,nmax=3,minfreq=2)
    extractor.statistical_term_extraction(minfreq=2)
    extractor.merge_term_frequencies(verbose=False)
    extractor.load_exclusion_regex("regex-eng.txt")
    extractor.regex_exclusion(verbose=False)
    extractor.nest_normalization(verbose=False)
    extractor.save_term_candidate_archivo("archivo_term_candidates")
    

if __name__ == "__main__":
    main()

