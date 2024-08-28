from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .kusto_cleaner import clean
import numpy as np


class Grouper():
    @staticmethod
    def group_by_tfidf(kusto_queries, similarity_threshold=0.7):
        cleaned_kusto_queries = [clean(q) for q in kusto_queries]
        tf_idf_matrix = Grouper.compute_tf_idf_matrix(cleaned_kusto_queries)
        cosine_sim_matrix = cosine_similarity(tf_idf_matrix)
        labels = [-1] * len(cleaned_kusto_queries)
        current_group_id = 0

        for i in range(len(cleaned_kusto_queries)):
            if labels[i] != -1:
                continue

            similar_queries = np.where(
                cosine_sim_matrix[i] >= similarity_threshold)[0]

            if len(similar_queries) > 1:
                for idx in similar_queries:
                    labels[idx] = current_group_id
                current_group_id += 1

        return labels

    @staticmethod
    def compute_tf_idf_matrix(queries):
        vectorizer = TfidfVectorizer(
            tokenizer=lambda x: x.split(), stop_words='english')
        return vectorizer.fit_transform(queries)
