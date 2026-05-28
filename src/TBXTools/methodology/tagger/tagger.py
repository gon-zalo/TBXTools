import sys
import subprocess
import spacy #attenta perché hai dovuto fare pip install- magari lo dovrai mettere tra i requirements

#class to perform pos tagging of a raw corpus

#maybe you'll need to change the en_core - prende questo di default
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
                print("Please restart the program to apply changes.")
                sys.exit(0)
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