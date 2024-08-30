import pandas as pd
from bertopic import BERTopic
from umap import UMAP
from sentence_transformers import SentenceTransformer
from pathlib import Path
import os

import json




if  __name__ == '__main__':


    umap_model_config3 = UMAP(
        n_components=30,
        n_neighbors=100,
        min_dist=0.1,
        metric="cosine",
        random_state=42
    )

    model = SentenceTransformer("sentence-transformers/distiluse-base-multilingual-cased-v2")

    dataset = pd.read_csv("headers_jupyter_dataset_top_1000_non_SE_purpose.csv")
    dataset = dataset.dropna()
    dataset['cleaned_header'] = dataset['cleaned_header'].astype(str)

    headers = dataset['cleaned_header'].to_list()

    topic_model_config3 = BERTopic(embedding_model=model,
                       calculate_probabilities=False,
                       verbose=True,
                       min_topic_size = 50,
                       umap_model=umap_model_config3)

    topics_config3, probs_config_3 = topic_model_config3.fit_transform(headers)
    print(f"*** fit completed. Starting visualization... ***")

    vis_topics = topic_model_config3.visualize_topics()

    vis_topics.write_html("config3_non_SE_purpose.html")

    print(f"*** visualization completed. Starting get topic info... ***")

    df_get_topic_info = pd.DataFrame(topic_model_config3.get_topic_info())
    df_get_topic_info.to_csv("get_topic_info_non_SE_purpose.csv")

    print(f"*** get topic info completed. Starting get topic info... ***")


    df_document_info =topic_model_config3.get_document_info(headers)
    df_document_info['url'] = dataset['url'].to_list()
    df_document_info['github_path'] = dataset['github_path'].to_list()
    df_document_info.to_csv("document_info_non_SE_purpose.csv")

    print(f"*** get document info completed. Starting get representative docs... ***")


    representative_docs = topic_model_config3.get_representative_docs(topic=None)
    
    with open('representative_docs_non_SE_purpose.json', 'w') as json_file:
        json.dump(representative_docs, json_file, indent=4)

    print(f"*** get representative document completed. Starting hierarchical topics... ***")


    hierarchical_topics = topic_model_config3.hierarchical_topics(headers)
    tree = topic_model_config3.get_topic_tree(hierarchical_topics)
    with open("tree_non_SE_purpose.txt", "w", encoding='utf-8') as f:
        print(tree, file=f)

    print(f"*** get hierarchical topics completed. Starting tree visualization... ***")


    vis_tree = topic_model_config3.visualize_hierarchy(hierarchical_topics=hierarchical_topics)
    vis_tree.write_html("tree_non_SE_purpose.html")

    print(f"*** Finished tree visualization. Starting visualizing documents...***")

    embeddings = model.encode(headers, show_progress_bar=True)

    fig_docs = topic_model_config3.visualize_documents(headers, embeddings=embeddings)
    fig_docs.write_html("docs_non_SE.html")

    print(f"*** End!***")
