from bs4 import BeautifulSoup
import spacy
import unidecode
from word2number import w2n
from collections import Counter
from nltk.corpus import wordnet as wn


simple_expand_contraction = True
nlp = spacy.load('en_core_web_sm')
# exclude words from spacy stopwords list
#for w in ['no', 'not', 'No', 'Not', 'NO', 'NOT']: 
#    nlp.vocab[w].is_stop = False


#======================================================

if simple_expand_contraction:
    import contractions
else:
    from pycontractions import Contractions
    import gensim.downloader as api
    # Choose model accordingly for contractions function
    model = api.load("glove-twitter-25")
    # model = api.load("glove-twitter-100")
    # model = api.load("word2vec-google-news-300")
    cont = Contractions(kv_model=model)
    cont.load_models()

def strip_html_tags(text):
    """remove html tags from text"""
    soup = BeautifulSoup(text, "html.parser")
    stripped_text = soup.get_text(separator=" ")
    return stripped_text


def remove_whitespace(text):
    """remove extra whitespaces from text"""
    text = text.strip()
    return " ".join(text.split())


def remove_accented_chars(text):
    """remove accented characters from text, e.g. café"""
    text = unidecode.unidecode(text)
    return text


def expand_contractions(text):
    """expand shortened words, e.g. don't to do not"""
    if simple_expand_contraction:
        text = contractions.fix(text)
    else:
        text = list(cont.expand_texts([text], precise=True))[0]
    return text


def text_preprocessing(text, accented_chars=True, contractions=True, 
                       convert_num=True, extra_whitespace=True, 
                       lemmatization=True, lowercase=True, punctuations=True,
                       remove_html=True, remove_num=True, special_chars=True, 
                       stop_words=True):
    """preprocess text with default option set to true for all steps"""
    if remove_html == True: #remove html tags
        text = strip_html_tags(text)
    if extra_whitespace == True: #remove extra whitespaces
        text = remove_whitespace(text)
    if accented_chars == True: #remove accented characters
        text = remove_accented_chars(text)
    if contractions == True: #expand contractions
        text = expand_contractions(text)
    if lowercase == True: #convert all characters to lowercase
        text = text.lower()

    doc = nlp(text) #tokenise text

    clean_text = []
    
    for token in doc:
        flag = True
        edit = token.text
        # remove stop words
        if stop_words == True and token.is_stop and token.pos_ != 'NUM': 
            flag = False
        # remove punctuations
        if punctuations == True and token.pos_ == 'PUNCT' and flag == True: 
            flag = False
        # remove special characters
        if special_chars == True and token.pos_ == 'SYM' and flag == True: 
            flag = False
        # remove numbers
        if remove_num == True and (token.pos_ == 'NUM' or token.text.isnumeric()) \
        and flag == True:
            flag = False
        # convert number words to numeric numbers
        if convert_num == True and token.pos_ == 'NUM' and flag == True:
            edit = w2n.word_to_num(token.text)
        # convert tokens to base form
        elif lemmatization == True and token.lemma_ != "-PRON-" and flag == True:
            edit = token.lemma_
        # append tokens edited and not removed to list 
        if edit != "" and flag == True:
            clean_text.append(edit)        
    return clean_text


def word_freq(corpus, ngram=[1,2,3,4], allow_word=['v', 'a']):
    # corpus: [text1, text2, ...]
    tokens = [text_preprocessing(t, remove_num=False, stop_words=False, convert_num=False) for t in corpus]
    all = []
    for n in ngram:
        all += sum([[tuple(s[i:i+n]) for i in range(len(s)-n+1)] for s in tokens if len(s) >= n], [])
    
    dout = dict()
    for x in sorted(Counter(all).items(), key=lambda e: -e[1]):
        flag = False
        if len(x[0]) == 1:
            if not nlp.vocab[x[0][0]].is_stop: flag = True
        else:
            for word in x[0]:
                tmp = wn.synsets(word)
                if (len(tmp)>0) and (tmp[0].pos() in allow_word):
                    flag = True
                    break
        if flag:
            dout[' '.join(x[0])] = x[1]
    return dout

