import pandas as pd
from bertopic import BERTopic
from umap import UMAP
from sentence_transformers import SentenceTransformer
from pathlib import Path
import os
import gensim
from gensim.models.coherencemodel import CoherenceModel

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


if  __name__ == '__main__':


    umap_model_config4 = UMAP(
        n_components=30,
        n_neighbors=100,
        min_dist=0.1,
        metric="cosine",
        random_state=42
    )

    #model = SentenceTransformer("sentence-transformers/distiluse-base-multilingual-cased-v2")
    model = SentenceTransformer("./model")
    dataset = pd.read_csv("active_non_SE_repos_headers.csv")
    dataset = dataset.dropna()
    dataset['cleaned_header'] = dataset['cleaned_header'].astype(str)

    headers = dataset['cleaned_header'].to_list()
    
    topic_model_config4 = BERTopic(embedding_model=model,
                       calculate_probabilities=False,
                       verbose=True,
                       min_topic_size = 50,
                       umap_model=umap_model_config4)

    topics_config4, probs_config_4 = topic_model_config4.fit_transform(headers)
    print(f"*** fit completed. ... ***")

    metrics = calculate_cv_metrics(topic_model_config4, topics_config4, headers)
    
    with open("metrics.txt", 'w') as f:
        print(metrics, file=f)

    print(f"*** Cv metrics completed. Starting visualizations...***")

    vis_topics = topic_model_config4.visualize_topics()

    vis_topics.write_html("config4_non_SE_purpose.html")

    print(f"*** visualization completed. Starting get topic info... ***")

    df_get_topic_info = pd.DataFrame(topic_model_config4.get_topic_info())
    df_get_topic_info.to_csv("get_topic_info_non_SE_purpose.csv")

    print(f"*** get topic info completed. Starting get topic info... ***")


    df_document_info =topic_model_config4.get_document_info(headers)
    df_document_info['url'] = dataset['url'].to_list()
    df_document_info['github_path'] = dataset['github_path'].to_list()
    df_document_info.to_csv("document_info_non_SE_purpose.csv")

    print(f"*** get document info completed. Starting get representative docs... ***")


    representative_docs = topic_model_config4.get_representative_docs(topic=None)
    
    with open('representative_docs_non_SE_purpose.json', 'w') as json_file:
        json.dump(representative_docs, json_file, indent=4)

    print(f"*** get representative document completed. Starting hierarchical topics... ***")


    hierarchical_topics = topic_model_config4.hierarchical_topics(headers)
    tree = topic_model_config4.get_topic_tree(hierarchical_topics)
    with open("tree_non_SE_purpose.txt", "w", encoding='utf-8') as f:
        print(tree, file=f)

    print(f"*** get hierarchical topics completed. Starting tree visualization... ***")


    vis_tree = topic_model_config4.visualize_hierarchy(hierarchical_topics=hierarchical_topics)
    vis_tree.write_html("tree_non_SE_purpose.html")

    print(f"*** Finished tree visualization. Starting visualizing documents...***")

    embeddings = model.encode(headers, show_progress_bar=True)

    fig_docs = topic_model_config4.visualize_documents(headers, embeddings=embeddings)
    fig_docs.write_html("docs_non_SE.html")

    print(f"*** End!***")
