# Topic Modeling

Codes used for inferring the themes/topics of Jupyter notebooks markdown headers. The runs were done in a cluster environment, since GPU is required. It takes around 30 minutes to run each topic modeling with the described configuration in the .sh files of this directory. 

## Installations and Runs

The preprocessing of the Jupyter notebook headers text was done in `preprocess.py`.


Check `bertopic_install.sh` for installation process for the topic modeling.
Check `all_active_repos_coherence.sh` for installations for calculating the topics coherence score. After that, run `download_sbert_mode.py` to have the language model downloaded for topic modeling.

The topic modeling for both the Software Engineer data split and for the Educational data split are done in `active_repos_with_coherence.py`. The input csv files (containing the markdown headers) should be updated in the code according to the desired split (SE or Educational). 

All results are generated: the number of total topics generated, coherence metrics, the dendogram (tree) that clusters smilar topics and related visualzations. The results were organized in the `results` directory. 

In the `results` directory is also possible to check the input files used (markdown headers). 

The manual clustering process of topic IDs can be seen in `merge_topics_tree.py`.