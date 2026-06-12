import sys
import subprocess
import spacy  #requirements?

#class to perform pos tagging of a raw corpus

class LinguisticTagger:
    '''Manages linguistic POS-tagging
    
    Attributes:
        model_name (str): The name of the spaCy model to load (e.g.,
          'en_core_web_sm').
        nlp (spacy.Language or None): The loaded spaCy pipeline instance used
          for tagging.
    '''
    def __init__(self, model_name="en_core_web_sm"):
        self.model_name = model_name
        self.nlp = None
        self._load_model()

    
    def _load_model(self): 
        """
        Checks for the spaCy model, downloading it via subprocess if missing, then loads it into self.nlp.

        Attributes:
            self.model_name (str): The name of the spaCy model to be loaded (e.g.,
          'en_core_web_sm').
        
        Raises:
            SystemExit: If the model download fails, the program terminates with an
            exit code of 1.
        
        """

        # Check if the spaCy model package is already installed in the system
        if not spacy.util.is_package(self.model_name):
            print(f"Downloading and installing spaCy model: {self.model_name}...")
            try:
                subprocess.check_call([sys.executable, "-m", "spacy", "download", self.model_name])
                print(f"\nModel {self.model_name} downloaded successfully.")
                
                #Note: Loading directly avoids a restart, but a manual rerun may still be required if the environment fails to refresh internal package links instantly.
                print(f"Initializing Tagger with the newly downloaded model: {self.model_name}")
                # Initialize the newly installed model
                self.nlp = spacy.load(self.model_name)

            except Exception as e:
                print(f"Error downloading model '{self.model_name}': {e}")
                # Terminate execution to prevent subsequent cascade errors in the pipeline
                sys.exit(1)
        else:
            # If the model is already installed, load it directly into memory
            print(f"Initializing POSTagger with model: {self.model_name}")
            self.nlp = spacy.load(self.model_name)
    

    def tag_segment(self, segment: str) -> str:
        """
        Tags a single segment and returns it in the 'word|lemma|POS' format, separated by tabs.

        Args:
        segment (str): The input text string to be processed.

        Returns:
        str: A tab-separated string of tokens, or an empty string if input is invalid.


        """
        if not segment or not self.nlp:
            return ""
            
        doc = self.nlp(segment)
        data = []
        for token in doc:
            if not token.is_space:
                data.append(f"{token.text}|{token.lemma_}|{token.pos_}")
        
        return " \t ".join(data) if data else ""