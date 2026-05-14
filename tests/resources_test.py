from TBXTools.resources import Resources

LANG_CODES = ["en", "es", "fr", "ca"]

for code in LANG_CODES:
    resources = Resources(lang_code=code)

    stopwords = resources.fetch_stopwords()
    stopwords = sorted(stopwords)
    print(f"Number of stopwords in {code.upper()}: {len(stopwords)}. First 5: {stopwords[:5]}")

    inner_stopwords = resources.fetch_inner_stopwords()
    inner_stopwords = sorted(inner_stopwords)
    print(f"Number of inner stopwords in {code.upper()}: {len(inner_stopwords)}. First 5: {inner_stopwords[:5]}\n")

# print(resources.fetch_regexes())