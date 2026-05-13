from TBXTools.resources import Resources

resources = Resources(lang_code="en")

print(resources.fetch_stopwords())
print(resources.fetch_inner_stopwords())

# print(resources.fetch_regexes())