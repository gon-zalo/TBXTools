from TBXTools._core.bilingual import BilingualExtractor 
from TBXTools.methodology import LinguisticMethodology 
from TBXTools.methodology import StatisticalMethodology

src_corpus_txt = "Mental_disorder.txt"
tgt_corpus_txt = "Trastorno_mental.txt"

src_corpus_moses = "piccolo.en"
tgt_corpus_moses = "piccolo.es"

corpus_tmx = "piccolo1.tmx"

corpus_tabtxt = "piccolo.tab"
corpus_tabtxt2 = "piccolo.tsv"

corpus_tabtxt_it = "selected-segments-en-it.tab"
corpus_tabtxt_es = "selected-segments-en-es.tab"

#corpus_sdltm - este falta

#solo statistical test 

#tuple da usare per file singoli:
# parallel_corpus=(src_corpus_moses, tgt_corpus_moses)
# parallel_corpus=(src_corpus_txt, tgt_corpus_txt)


bilingual_extractor = BilingualExtractor(
    project_name="parallel_project",
    src_methodology= StatisticalMethodology(
        nmin=2,
        nmax=3,
        case_normalization=True
    ),
    tgt_methodology= StatisticalMethodology(
        nmin=2,
        nmax=3,
        case_normalization=True
    ),
    src_language="en",
    tgt_language="es",
    parallel_corpus=(src_corpus_moses, tgt_corpus_moses),
    overwrite_project=True
)

bilingual_results = bilingual_extractor.extract(verbose=True)

src_terms = [row[0] for row in bilingual_results.src._terms]
tgt_terms = [row[0] for row in bilingual_results.tgt._terms]

print(f"\nSource language terms: {len(src_terms)}")
print(f"Target language terms: {len(tgt_terms)}")

bilingual_results.align(synonym=False)

bilingual_results.save_aligned_candidates("prova.json", reverse=True)
bilingual_results.save_aligned_candidates("prova.txt", reverse=True)
bilingual_results.save_aligned_candidates("prova.jsonl")
bilingual_results.save_aligned_candidates("prova.xlsx")
bilingual_results.save_aligned_candidates("prova.csv")


#bilingual_results.src.nest_normalization()



