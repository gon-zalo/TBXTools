import sys
import subprocess
import spacy  #requirements?

#class to perform pos tagging of a raw corpus

#where do you want to put it? 
def get_model_from_code(lang_code):
        """
        Takes a language code and returns the correct spaCy model name.
        """
        spacy_models = {
        "en": "en_core_web_sm",
        "ca": "ca_core_news_sm",
        "fr": "fr_core_news_sm",
        "es": "es_core_news_sm"
        }
    
    #maybe we don´t need a default one- discuss!
        return spacy_models.get(lang_code, "en_core_web_sm")

class LinguisticTagger:
    def __init__(self, model_name="en_core_web_sm"):
        self.model_name = model_name
        self.nlp = None
        self._load_model()

    
    #you know how it works- maybe add some comments
    def _load_model(self): 
        """To load the model"""
        if not spacy.util.is_package(self.model_name):
            print(f"Downloading and installing spaCy model: {self.model_name}...")
            try:
                subprocess.check_call([sys.executable, "-m", "spacy", "download", self.model_name])
                print(f"\nModel {self.model_name} downloaded successfully.")
                
                #Note: Loading directly avoids a restart, but a manual rerun may still be required if the environment fails to refresh internal package links instantly.
                print(f"Initializing Tagger with the newly downloaded model: {self.model_name}")
                self.nlp = spacy.load(self.model_name)

            except Exception as e:
                print(f"Error downloading model '{self.model_name}': {e}")
                sys.exit(1)
        else:
            print(f"Initializing POSTagger with model: {self.model_name}")
            self.nlp = spacy.load(self.model_name)
    

    def tag_segment(self, segment: str) -> str:
        """
        Tags a single segment and returns it in the 'word|lemma|POS' format, separated by tabs.
        """
        if not segment or not self.nlp:
            return ""
            
        doc = self.nlp(segment)
        data = []
        for token in doc:
            if not token.is_space:
                data.append(f"{token.text}|{token.lemma_}|{token.pos_}")
        
        return " \t ".join(data) if data else ""