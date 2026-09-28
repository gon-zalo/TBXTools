from xml.etree import ElementTree as etree
from TBXTools._utils.utils import get_lang
from pathlib import Path

class FileParser:
    
    def __init__(self, src_lang, tgt_lang):
        self.src_lang = src_lang
        self.tgt_lang = tgt_lang

    def parse_corpus(self, corpus):
        if isinstance(corpus, (tuple, list)) and len(corpus) == 2: # parsing moses or 2 separate txt files
            src_file, tgt_file = corpus
            
            src_corpus = self._parse_txt(src_file)
            tgt_corpus = self._parse_txt(tgt_file)

        else: # parsing tsv and tmx
            ext = Path(corpus).suffix.lower()
            if ext in [".tab", ".tsv"]:
                src_corpus, tgt_corpus = self._parse_tab(corpus)

            elif ext == ".tmx":
                src_corpus, tgt_corpus = self._parse_tmx(corpus)
            else:
                raise ValueError(f"Unsupported file format: {ext}. Supported formats: moses, txt, tsv and tmx")

        return src_corpus, tgt_corpus
    
    def _parse_tmx(self, file_path):
            src_list, tgt_list = [], []
        
            _, src_iso = get_lang(str(self.src_lang).lower())
            _, tgt_iso = get_lang(str(self.tgt_lang).lower())
            
            xml_lang = "{http://www.w3.org/XML/1998/namespace}lang"
    
            for event, elem in etree.iterparse(str(file_path), events=("end",)):
                if elem.tag == "tu":
                    s_text, t_text = None, None
                    for tuv in elem.findall("tuv"):
                        l_attr = (tuv.attrib.get(xml_lang) or tuv.attrib.get("lang") or "").lower().strip()
                        seg = tuv.find("seg")
                        if seg is not None and seg.text and seg.text.strip():
                            if l_attr.startswith(src_iso):
                                s_text = seg.text.strip()
                            elif l_attr.startswith(tgt_iso):
                                t_text = seg.text.strip()
                    
                    if s_text and t_text:
                        src_list.append(s_text)
                        tgt_list.append(t_text)
                    elem.clear()
                    
            return src_list, tgt_list
                    
    def _parse_tab(self, file_path, encoding="utf-8"):
            src_list, tgt_list = [], []
            with open(str(file_path), "r", encoding=encoding, errors="ignore") as cf:
                for linia in cf:
                    linia = linia.rstrip("\r\n").strip()
                    if not linia:
                        continue
    
                    camps = linia.split("\t") 
                    if len(camps) >= 2:
                        src_list.append(camps[0].strip())
                        tgt_list.append(camps[1].strip())
                        
            return src_list, tgt_list    
    
    def _parse_txt(self, file_path, encoding="utf-8"):
        corpus = []
        with open(str(file_path), "r", encoding=encoding, errors="ignore") as f:
            for line in f:
                clean_line = line.strip()
                if clean_line:
                    corpus.append(clean_line)
        return corpus  