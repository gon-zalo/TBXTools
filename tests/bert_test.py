from TBXTools import Extractor, BertExtractor

extractor = Extractor(
    project_name="bert-test",
    method=BertExtractor(),
    corpus='Mental_health.txt'
)

extractor.extract()

print(extractor.terms())
print(extractor.tokens())
