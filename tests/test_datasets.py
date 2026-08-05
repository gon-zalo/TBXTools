from TBXTools.datasets import load_detech26

detech = load_detech26(split="test", to_pandas=False)

for line in detech.terms():
    print(line)
