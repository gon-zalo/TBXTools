def get_lang(language):
    '''
    Takes a language name, two letter code or three letter code to return the name and the code.

    Returns:
        language_name: The name of the language in English.
        language_code: The ISO 639-1 language code (e.g. 'en').
    '''
    import pycountry
    if len(language) == 2: # if language is 2 letter iso code
        language_pyc = pycountry.languages.get(alpha_2=language)
        language_code = language_pyc.alpha_2
        language_name = language_pyc.name

    elif len(language) == 3:
        language_pyc = pycountry.languages.get(alpha_3=language)

        if language_pyc:
            language_code = language_pyc.alpha_2 if hasattr(language_pyc, 'alpha_2') else language_pyc.alpha_3
            language_name = language_pyc.name

    elif len(language) > 3: # if language is the name of the language
        for lang in pycountry.languages:
            if lang.name.lower() == language.lower():
                language_pyc = pycountry.languages.get(name=language)
                language_code = language_pyc.alpha_2
                language_name = language_pyc.name

    return language_name, language_code

def get_spacy_model_from_code(lang_code):
        """
        Takes a language code and returns the correct spaCy model name.

        Args:
          lang_code: the ISO language code

        Returns:
          The corresponding spaCy model name.
        """
        if not lang_code:
             return None
        
        if lang_code == "en":
             return "en_core_web_sm"
        
        return f"{lang_code}_core_news_sm"


def load_spacy_model(model_name): 
        """
        Checks for the spaCy model, downloading it via subprocess if missing, then loads it into self.nlp.

        Args:
            model_name (str): The name of the spaCy model to be loaded (e.g.,'en_core_web_sm').
        
        Raises:
            SystemExit: If the model download fails, the program terminates with an
            exit code of 1.
        """
        import spacy
        import subprocess
        import sys

        if not spacy.util.is_package(model_name):
            print(f"Downloading and installing spaCy model: {model_name}...")
            try:
                subprocess.check_call([sys.executable, "-m", "spacy", "download", model_name])
                print(f"\nModel {model_name} downloaded successfully.")

                nlp = spacy.load(model_name)

            except Exception as e:
                print(f"Error downloading model '{model_name}': {e}")
                sys.exit(1)
        else:
            nlp = spacy.load(model_name)
        
        return nlp


def merge_databases(new_db_path, db_paths):
    '''
    Merges SQLite databases, where each extraction project is stored, into one database. This is especially useful with the BERT methodology. You can annotate data in different languages or domains and then merge them all into one database to train a unique model with.
    '''
    import sqlite3
    import shutil
    if len(db_paths) == 0:
        raise ValueError("The list of database paths is empty.")
        
    elif len(db_paths) == 1:
        raise ValueError(f"You need to pass 2 or more databases to merge")

    elif not isinstance(db_paths, list):
        raise ValueError(f"You need to pass a list of databases: ['db1.sqlite', 'db2.sqlite']")
    
    elif len(db_paths) > 1 and isinstance(db_paths, list):
        shutil.copy2(db_paths[0], new_db_path) # copies the first db into the new one
        print(f"Initialized {new_db_path} using {db_paths[0]}")
        conn = sqlite3.connect(new_db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = [row[0] for row in cursor.fetchall()]
            
            for db_path in db_paths[1:]: # continues merging dbs from the second one, since the first one was already copied
                print(f"Merging database: {db_path}...")
                
                try:
                    cursor.execute(f"ATTACH DATABASE '{db_path}' AS current_merge_db")

                    for table in tables:
                        cursor.execute(f"PRAGMA table_info({table})")
                        columns = [row[1] for row in cursor.fetchall() if row[5] == 0]
                        cols_string = ", ".join(columns)

                        try:
                            cursor.execute(f"INSERT INTO {table} ({cols_string}) SELECT {cols_string} FROM current_merge_db.{table}")

                        except sqlite3.OperationalError:
                            print(f"  -> Skipped table '{table}' (Not found in {db_path})")
                    
                    conn.commit()
                    
                except sqlite3.Error as e:
                    print(f"Failed to attach/process {db_path}: {e}")
                    
                finally:
                    cursor.execute("DETACH DATABASE current_merge_db")

            print(f"\nAll databases fully merged into {new_db_path}")

        except sqlite3.Error as e:
            print(f"A critical error occurred: {e}")

        finally:
            conn.close()