import nltk
from nltk.util import ngrams
from nltk.probability import FreqDist

class StatisticalExtractor:

    def __init__(self):
        self.n_grams = None
        self.tokens = None

    def ngram_calculation (self, segments, n_min, n_max, minfreq=2, corpus=None):
        '''Performs the calculation of ngrams.'''
        
        ngramsFD= FreqDist()
        tokensFD= FreqDist()
        n_min = n_min
        n_max = n_max
            
        for segment in segments:
            # print(segment)
            for n in range(n_min, n_max+1): #we DON'T calculate one order bigger in order to detect nested candidates

                tokens = segment.split() # tokenizing here, can be done separately
                # print(tokens)
                ngs = ngrams(tokens, n)

                for ng in ngs:
                    ngramsFD[ng] += 1

            for token in tokens:
                tokensFD[token] += 1

        n_grams = []
        for c in ngramsFD.most_common():
            if c[1]>=minfreq:

                record=[] # change
                record.append(" ".join(c[0]))            
                record.append(len(c[0]))
                record.append(c[1])   
                n_grams.append(record)

        self.n_grams = n_grams

        tokens_output = []                
        for c in tokensFD.most_common():
            record=[]
            record.append(c[0])            
            record.append(c[1])   
            tokens_output.append(record)

        self.tokens = tokens_output

        return n_grams, tokens_output

    def statistical_term_extraction(self,minfreq=2,corpus="sl_corpus"):
        '''Performs an statistical term extraction using the extracted ngrams (ngram_calculation should be executed first). Loading stop-words is advisable. '''
        self.cur.execute("DELETE FROM term_candidates")
        self.conn.commit()
        stopwords=[]
        with self.conn:
            if corpus=="sl_corpus":
                self.cur.execute("SELECT sl_stopword FROM sl_stopwords")
            elif corpus=="tl_corpus":
                self.cur.execute("SELECT tl_stopword FROM tl_stopwords")
            for s in self.cur.fetchall():
                stopwords.append(s[0])
                
        inner_stopwords=[]
        with self.conn:
            if corpus=="sl_corpus":
                self.cur.execute("SELECT sl_inner_stopword FROM sl_inner_stopwords")
            elif corpus=="tl_corpus":
                self.cur.execute("SELECT tl_inner_stopword FROM tl_inner_stopwords")
            for s in self.cur.fetchall():
                inner_stopwords.append(s[0])
        
        self.cur.execute("SELECT ngram, n, frequency FROM ngrams order by frequency desc")
        results=self.cur.fetchall()
        data=[] 
        for a in results:
            if corpus=="sl_corpus":
                if self.specificSLtokenizer:
                    ng=self.SLtokenizer.tokenize(a[0]).split()
                else:
                    ng=a[0].split()
            if corpus=="tl_corpus":
                if self.specificTLtokenizer:
                    
                    ng=self.TLtokenizer.tokenize(a[0]).split()
                else:
                    ng=a[0].split()
            include=True
            if ng[0].lower() in stopwords: include=False
            if ng[-1].lower() in stopwords: include=False
            for i in range(1,len(ng)):
                if ng[i].lower() in inner_stopwords:
                    include=False
            if include:
                record=[]
                record.append(a[0])            
                record.append(a[1])
                record.append(a[2])
                record.append("freq")
                record.append(a[2])   
                data.append(record)
            if a[2]<minfreq:
                break
        with self.conn:
            self.cur.executemany("INSERT INTO term_candidates (candidate, n, frequency, measure, value) VALUES (?,?,?,?,?)",data)        
            self.conn.commit()