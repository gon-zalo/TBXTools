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

#linguistic 

#Linguistic Methodology

evaluation_terms = "evaluation_terms.txt"
es_evaluation_terms = "evaluation_terms_spanish.txt"


bilingual_extractor = BilingualExtractor(
    project_name="parallel_project",
    src_methodology= LinguisticMethodology(
        nmin=2,
        nmax=3,
        case_normalization=True,
        is_corpus_tagged=False,
        evaluation_terms=evaluation_terms
    ),
    tgt_methodology= LinguisticMethodology(
        nmin=2,
        nmax=3,
        case_normalization=True,
        is_corpus_tagged=False,
        evaluation_terms=es_evaluation_terms
    ),
    src_language="en",
    tgt_language="es",
    parallel_corpus=corpus_tabtxt_es,
    overwrite_project=True
)

bilingual_results = bilingual_extractor.extract(verbose=True)
#bilingual_results.src_results.nest_normalization(percent=10, verbose=True) - ejemplo de como funcionará la clase bilingual results cuando implementarás los otros filtros y todos los metodos que ya había en la clase Results


src_terms = [row[0] for row in bilingual_results.src._terms]
tgt_terms = [row[0] for row in bilingual_results.tgt._terms]

print(f"\nSource language terms: {len(src_terms)}")
print(f"Target language terms: {len(tgt_terms)}")
