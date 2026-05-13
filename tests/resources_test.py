from TBXTools.resources import Resources

resources = Resources()

print(resources.fetch_stopwords_file("en"))
print(resources.fetch_inner_stopwords_file("en"))
print(resources.fetch_regexes_file("en"))