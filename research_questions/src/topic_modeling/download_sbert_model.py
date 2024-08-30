from bertopic import BERTopic
from sentence_transformers import SentenceTransformer

model = SentenceTransformer(
    "sentence-transformers/distiluse-base-multilingual-cased-v2")
model.save("./model")
