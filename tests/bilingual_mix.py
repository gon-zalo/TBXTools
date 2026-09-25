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

#corpus_sdltm - este falta

#solo statistical test 

#tuple da usare per file singoli:
# parallel_corpus=(src_corpus_moses, tgt_corpus_moses)
# parallel_corpus=(src_corpus_txt, tgt_corpus_txt)

evaluation_terms = "evaluation_terms.txt"
es_evaluation_terms = "evaluation_terms_spanish.txt"

bilingual_extractor = BilingualExtractor(
    project_name="parallel_project",
    src_methodology= StatisticalMethodology(
        nmin=2,
        nmax=3,
        case_normalization=True
    ),
    tgt_methodology= LinguisticMethodology(
        nmin=2,
        nmax=3,
        case_normalization=True,
        is_corpus_tagged=False,
        linguistic_patterns="ling_pat-es.txt"
    ),
    src_language="en",
    tgt_language="es",
    parallel_corpus=corpus_tmx,
    overwrite_project=True
)

bilingual_results = bilingual_extractor.extract(verbose=True)
#bilingual_results.src_results.nest_normalization(percent=10, verbose=True) - ejemplo de como funcionará la clase bilingual results cuando implementarás los otros filtros y todos los metodos que ya había en la clase Results

src_terms = [row[0] for row in bilingual_results.src._terms]
tgt_terms = [row[0] for row in bilingual_results.tgt._terms]

print(f"\nSource language terms: {len(src_terms)}")
print(f"Target language terms: {len(tgt_terms)}")