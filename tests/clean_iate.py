import pandas as pd

iate = "IATE_export.csv"

df = pd.read_csv(iate, sep="|")

df = df[["E_ID", "T_TERM", "L_CODE"]]

# en_df = df[df["L_CODE"] == "en"].reset_index(drop=True)

pl_df = df[df["L_CODE"] == "pl"].reset_index(drop=True)

# merged_df = pd.merge(en_df, pl_df, on="E_ID")
pl_terms = pl_df["T_TERM"]

pl_terms.to_csv("pl_iate.txt", index=False, header=False)