from gensim.models.coherencemodel import CoherenceModel
import pandas as pd
from bertopic import BERTopic
from pathlib import Path
import os
import json

def _coherence_score_BERTopic(model, model_topics, texts, coherence_type):

    documents = pd.DataFrame({"Document": texts,
                            "ID": range(len(texts)),
                            "Topic": model_topics})
    documents = documents[documents['Document'] != ""]
    texts = [doc for doc in texts if (doc and doc !="")]



    documents_per_topic = documents.groupby(['Topic'], as_index=False).agg({'Document': ' '.join})
    cleaned_texts = model._preprocess_text(documents_per_topic.Document.values)


    # Extract vectorizer and analyzer from BERTopic
    vectorizer = model.vectorizer_model
    analyzer = vectorizer.build_analyzer()

    # Extract features for Topic Coherence evaluation
    words = vectorizer.get_feature_names_out()
    tokens = [analyzer(doc) for doc in cleaned_texts]
    dictionary = gensim.corpora.Dictionary(tokens)
    corpus = [dictionary.doc2bow(token) for token in tokens]

    topic_words = [[words for words, _ in model.get_topic(topic)] 
                for topic in range(len(set(model_topics))-1)]

    topic_words = [[words for words, _ in model.get_topic(topic) if words!=''] 
                for topic in range(len(set(model_topics))-1)]

    topic_words = [word for word in topic_words if word]
    # https://github.com/RaRe-Technologies/gensim/issues/3328
    #  Coherence metrics use Pointwise Mutual Information (PMI), which means that to compute the coherence of a topic 
    # you need at least two words in the topic itself (to measure the NPMI using their co-occurrences) if you have 
    # only one word/id in a topic list, you're not gonna be able to compute the coherence, hence the nan.
    new_topic_words = []

    for i, topic in enumerate(topic_words):
        a = len([w for w in topic if w in dictionary.token2id])
        if a <= 1:
            print("index of the topic that should be removed: "+ str(i))
            print()
        else:
            new_topic_words.append(topic) 

    # Evaluate
    if coherence_type == "c_v":

        bertopic_coherence_model = CoherenceModel(topics=topic_words, texts=tokens, corpus=corpus, dictionary=dictionary, coherence=coherence_type)

    else:
        bertopic_coherence_model = CoherenceModel(topics=new_topic_words, texts=tokens, corpus=corpus, dictionary=dictionary, coherence=coherence_type)


    coherence_value = bertopic_coherence_model.get_coherence()
    print("coherence value:")

    return coherence_value


def calculate_cv_metrics(model, model_topics, texts):

    cv_score = _coherence_score_BERTopic(model, model_topics, texts, 'c_v') 
    umass_score = _coherence_score_BERTopic(model, model_topics, texts, 'u_mass') 
    c_uci_score = _coherence_score_BERTopic(model, model_topics, texts, 'c_uci')  
    c_npmi_score = _coherence_score_BERTopic(model, model_topics, texts, 'c_npmi') 

    coherence_scores = {'cv': cv_score,
                        'umass': umass_score,
                        'c_uci': c_uci_score,
                        'c_npmi': c_npmi_score}

    return coherence_scores
