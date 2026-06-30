def get_lang(language):
    import pycountry
    # input is iso 2 letter code or full name of the language, output is name and 2 letter iso code
    if len(language) == 2: # if language is 2 letter iso code
        language_pyc = pycountry.languages.get(alpha_2=language)
        language_code = language_pyc.alpha_2
        language_name = language_pyc.name

    elif len(language) == 3:
        language_pyc = pycountry.languages.get(alpha_3=language)
        language_name = language_pyc.name

        if language_pyc:
            language_code = language_pyc.alpha_2 if hasattr(language_pyc, 'alpha_2') else language_pyc.alpha_3

    elif len(language) > 3: # if language is the name of the language
        for lang in pycountry.languages:
            if lang.name.lower() == language.lower():
                language_pyc = pycountry.languages.get(name=language)
                language_code = language_pyc.alpha_2
                language_name = language_pyc.name

    return language_name, language_code

def get_model_from_code(lang_code):
        """
        Takes a language code and returns the correct spaCy model name.

        Args:
          lang_code: the language ISO code

        Returns:
          The corresponding spaCy model name.
        """
        spacy_models = {
        "en": "en_core_web_sm",
        "ca": "ca_core_news_sm",
        "fr": "fr_core_news_sm",
        "es": "es_core_news_sm"
        }
    
        return spacy_models.get(lang_code, None)

# maybe for the future
def check_required_data(required_data, sqlite_tables_loaded, name):

    for table in required_data:
        # if required data has not been loaded
        if table not in sqlite_tables_loaded:

            raise RuntimeError(f"Missing '{table}' data in database. You must provide the '{table}' argument to {name}.")