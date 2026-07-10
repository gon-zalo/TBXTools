from TBXTools import Extractor, StatisticalMethodology

regexes = [".+ health"]
# Se hai regex o termini TSR specifici per lingua, puoi sdoppiarli, 
# altrimenti se sono generici tieni questi.
tsr_terms = "tsr_terms.txt" 

# Configura i dati delle due lingue in una struttura pulita
language_config = {
    "english": {
        "corpus": "Mental_disorder.txt",
        "project": "statistical-example-en"
    },
    "spanish": {
        "corpus": "Trastorno_mental.txt",
        "project": "statistical-example-es"
    }
}

# Questo dizionario conterrà i risultati finali divisi per lingua
termini_estratti = {}

for language, data in language_config.items():
    
    extractor = Extractor(
        methodology=StatisticalMethodology(
            nmin=2,
            nmax=3,
            case_normalization=True
        ),
        project_name=data["project"],
        corpus=data["corpus"],
        language=language,          
        overwrite_project=True,
    )

    # 2. Estrazione dei risultati pesanti
    results = extractor.extract(verbose=False)

    # 3. Post-elaborazione e Filtri
    results.nest_normalization(verbose=False)
    results.regex_exclusion(regexes=regexes, verbose=False)

    # 4. Salviamo la lista finale dei termini nel nostro dizionario
    termini_estratti[lingua] = results.terms(limit=None)

# --- FINE DEL CICLO ---
# Ora hai estratto tutto. Puoi ispezionare i risultati separatamente:

print("\n================ RISULTATI FINALI ================")
print(f"Termini Inglesi trovati: {len(termini_estratti['english'])}")
print(f"Esempi Inglese: {termini_estratti['english'][:5]}") # Primi 5 termini

print(f"\nTermini Italiani trovati: {len(termini_estratti['spanish'])}")
print(f"Esempi Italiano: {termini_estratti['spanish'][:5]}") # Primi 5 termini