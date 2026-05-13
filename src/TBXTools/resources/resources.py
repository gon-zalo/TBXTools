from pathlib import Path
import inspect

class Resources:

    def __init__(self):
        
        self.resources_path = Path(inspect.getfile(Resources)).parent
        self.stopwords_path = self.resources_path /  "stopwords"
        self.inner_stopwords_path = self.resources_path / "inner"
        self.exclusion_regexes_path = self.resources_path / "regexes"

    def fetch_stopwords_file(self, lang_code):
        for file in self.stopwords_path.rglob("*.txt"):
            if file.stem.endswith(lang_code):

                return file

    def fetch_inner_stopwords_file(self, lang_code):
        for file in self.inner_stopwords_path.rglob("*.txt"):
            if file.stem.endswith(lang_code):

                return file
            
    def fetch_regexes_file(self, lang_code):
        for file in self.exclusion_regexes_path.rglob("*.txt"):
            if file.stem.endswith(lang_code):

                return file