from TBXTools import Extractor, StatisticalExtractor

extractor = Extractor(
    method=StatisticalExtractor(
        nmin=2,
        nmax=3),
    project_name="test",
    corpus="Mental_health.txt",
    language="en", 
    overwrite_project=True
)
new_stopwords = ["panadero", "hola", "test"]

print(" \nSTOPWORDS")
stopwords = extractor.stopwords()
print(len(stopwords))

extractor.add_stopwords(new_stopwords)
stopwords = extractor.stopwords()
print("\nAfter adding stopwords:")
print(len(stopwords))

print(" \nINNER STOPWORDS")
inner = extractor.inner_stopwords()
print(inner)
print(len(inner))

extractor.add_inner_stopwords(new_stopwords)
inner = extractor.inner_stopwords()
print("\nAfter adding inner stopwords:")
print(inner)
print(len(inner))