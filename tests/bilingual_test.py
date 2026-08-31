from TBXTools._core.bilingual_extractor import BilingualExtractor 
from TBXTools.methodology import LinguisticMethodology 
from TBXTools.methodology import StatisticalMethodology

#linguistic_patterns="ling_pat-en.txt" #questo poi in caso per il linguistic

src_corpus_txt = "Mental_disorder.txt"
tgt_corpus_txt = "Trastorno_mental.txt"

src_corpus_moses = "piccolo.en"
tgt_corpus_moses = "piccolo.es"

corpus_tmx = "piccolo1.tmx"

corpus_tabtxt = "piccolo.tab"
corpus_tabtxt2 = "piccolo.tsv"

#corpus_sdltm - este falta

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
    src_corpus=src_corpus_txt,
    tgt_corpus=tgt_corpus_txt,
    overwrite_project=True
)

bilingual_results = bilingual_extractor.extract(verbose=True)
#bilingual_results.src_results.nest_normalization(percent=10, verbose=True) - ejemplo de como funcionará la clase bilingual results cuando implementarás los otros filtros y todos los metodos que ya había en la clase Results

src_terms = [row[0] for row in bilingual_results.src_results._terms]
tgt_terms = [row[0] for row in bilingual_results.tgt_results._terms]

print(f"\nSource language terms: {len(src_terms)}")
print(f"Target language terms: {len(tgt_terms)}")