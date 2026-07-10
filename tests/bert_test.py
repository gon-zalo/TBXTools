from TBXTools import Extractor, BertMethodology
import pandas as pd

test_model = 'wmt-termlgy-test' # fine-tuned bert
expand_false = "wmt-termlgy-test-expandFalse"

eval_df = pd.read_csv("eval_df_bert-train-test-expandFalse.sqlite.csv")
eval_df["text"].to_csv("eval_corpus.txt", index=False, header=False)

methodology = BertMethodology(
    model=expand_false,
    labels="bio"
)

extractor = Extractor(
    project_name="bert-eval-test",
    methodology=methodology,
    corpus="eval_corpus.txt",
    language="english",
    overwrite_project=True
)

results = extractor.extract(verbose=False)

# print(results.terms(limit=None))
results.save_candidates("candidates-test-bert-expandFalse.txt", )