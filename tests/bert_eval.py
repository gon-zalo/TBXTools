from TBXTools import Extractor
from TBXTools.methodology import BertMethodology

# models
roberta_ap = "wmt-roberta-allpositive-ate"
large_ap = "wmt-robertalarge-allpositive-ate"

# eval data
engitech_en = "segments/sample-mechanical-engineering-en.txt"
medicine_en = "segments/sample-medicine-en.txt"

engitech_pl = "segments/sample-mechanical-engineering-pl.txt"
medicine_pl = "segments/sample-medicine-pl.txt"

#####
methodology = BertMethodology(
    model=roberta_ap, 
    labels="bio")

extractor = Extractor(
    project_name="wmt-bert-eval",
    methodology=methodology,
    corpus=engitech_pl,
    language="pl",
    overwrite_project=True)

extractor.add_stopwords(["—"]) # need to add this to string punct

results = extractor.extract()
results.normalize_declension()

results.save_candidates("wmt-roberta-engitech-terms-pl.csv")