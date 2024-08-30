import pandas as pd
from bertopic import BERTopic
from umap import UMAP
from sentence_transformers import SentenceTransformer
from pathlib import Path
import os
import json

from coherence_scores import calculate_cv_metrics



if  __name__ == '__main__':


    umap_model_config4 = UMAP(
        n_components=30,
        n_neighbors=15,
        min_dist=0.1,
        metric="cosine",
        random_state=42
    )

    model = SentenceTransformer("sentence-transformers/distiluse-base-multilingual-cased-v2")

    dataset = pd.read_csv("markdown_headers_dataset_jupyter_notebooks_top_1000.csv")
    dataset = dataset.dropna()
    dataset = dataset.loc[dataset['is_active'] == 'y']
    dataset['cleaned_header'] = dataset['cleaned_header'].astype(str)

    headers = dataset['cleaned_header'].to_list()

    topic_model_config4 = BERTopic(embedding_model=model,
                       calculate_probabilities=False,
                       verbose=True,
                       min_topic_size = 10,
                       umap_model=umap_model_config4)

    topics_config4, probs_config_3 = topic_model_config4.fit_transform(headers)
    print(f"*** fit completed. Calculating cv metrics... ***")

    metrics = calculate_cv_metrics(topic_model_config4, topics_config4, headers)
    print(f"*** Cv metrics completed. Starting visualization... ***")

    vis_topics = topic_model_config4.visualize_topics()

    vis_topics.write_html("config4_active_repos.html")

    print(f"*** visualization completed. Starting get topic info... ***")

    df_get_topic_info = pd.DataFrame(topic_model_config4.get_topic_info())
    df_get_topic_info.to_csv("get_topic_info_active_repos.csv")

    print(f"*** get topic info completed. Starting get topic info... ***")


    df_document_info =topic_model_config4.get_document_info(headers)
    df_document_info['url'] = dataset['url'].to_list()
    df_document_info['github_path'] = dataset['github_path'].to_list()
    df_document_info.to_csv("document_info_active_repos.csv")

    print(f"*** get document info completed. Starting get representative docs... ***")


    representative_docs = topic_model_config4.get_representative_docs(topic=None)
    
    with open('representative_docs_active_repos.json', 'w') as json_file:
        json.dump(representative_docs, json_file, indent=4)

    print(f"*** get representative document completed. Starting hierarchical topics... ***")


    hierarchical_topics = topic_model_config4.hierarchical_topics(headers)
    tree = topic_model_config4.get_topic_tree(hierarchical_topics)
    with open("tree_active_repos.txt", "w", encoding='utf-8') as f:
      print(tree, file=f)

    print(f"*** get hierarchical topics completed. Starting tree visualization... ***")


    vis_tree = topic_model_config4.visualize_hierarchy(hierarchical_topics=hierarchical_topics)
    vis_tree.write_html("tree_active_repos.html")

    print(f"*** Finished tree visualization. Starting visualizing documents...***")

    embeddings = model.encode(headers, show_progress_bar=True)

    fig_docs = topic_model_config4.visualize_documents(headers, embeddings=embeddings)
    fig_docs.write_html("docs_active_repos.html")

    print(f"*** End!***")
