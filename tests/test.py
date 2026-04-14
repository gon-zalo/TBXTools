from TBXTools import TerminologyExtractor, CustomPreprocessor

extractor = TerminologyExtractor()

extractor.process()
extractor.extract()
extractor.process(case_normalization=True)

extractor.case_normalization()