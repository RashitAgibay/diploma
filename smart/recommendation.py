from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import pandas as pd
import os

# TODO make independent from location of project
path = str(os.getcwdb().decode("utf-8").replace('\\', '/'))


class Recommendations:
    """
        Class for get, set, update, create our model - Content Based
        result: already trained data for get results
        ds: dataset for train
        stopwords: Stopwords of current Language for remove from content.
        result_path: Path of results where already trained data in csv format(for how is csv next
                     versions we will use Apache Cassandra)

    """

    def __init__(self, ds=[], stopwords=[]):
        self.results = {}
        self.ds = ds
        self.stopwords = stopwords
        self.result_path = path + "/smart/data/rec_results.csv"

    def content_based(self, description="description", item_id="id"):
        """

        Args:
            description: product description title in dataset
            item_id: product Identifier in dataset
        Actions:
            Convert a collection of Products to a matrix of TF-IDF features.

        Returns:
            None
        """

        tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 3), min_df=0, stop_words=self.stopwords)
        tfidf_matrix = tf.fit_transform(self.ds[description])
        # Cosine Similarities
        cs = linear_kernel(tfidf_matrix, tfidf_matrix)

        for r_id, row in self.ds.iterrows():
            similar_indices = cs[r_id].argsort()[:-100:-1]
            similar_items = [(cs[r_id][i], self.ds[item_id][i]) for i in similar_indices]
            self.results[row[item_id]] = similar_items[1:]
        self.result_writer()

    def result_writer(self):
        """
        Actions:
            Creates and writes Similarity results of  Item-to-Item
        Returns:
            None
        """
        csv_columns = ['id', 'score', 'rec_id']
        try:
            with open(self.result_path, 'w') as r_file:
                r_file.write("%s,%s,%s\n" % (csv_columns[0], csv_columns[1], csv_columns[2]))
                for key in self.results.keys():
                    for result in self.results[key]:
                        r_file.write("%s,%s,%s\n" % (key, result[0],result[1]))
        except IOError:
            print("I/O error")

    def get_results(self):
        """

        Returns:
            results DataFrame or CSV
        """
        return self.results

    def item(self, item_id):
        """

        Args:
            item_id: Id of Product

        Returns:
            Description of products by item_id
        """
        return self.ds.loc[self.ds['id'] == item_id]['description'].tolist()[0]

    def recommend(self, item_id, size=3):
        """
        Now not Usable
        Args:
            item_id:
            size:

        Returns:

        """
        recommendations = self.results[item_id][:size]
        return recommendations

    def get(self, item_id, size):
        """

        Args:
            item_id: Current product id
            size: How many products needs for Store Recommendation Section

        Returns:
            {
                'id': 'score',
                'id': 'score'
            }

             Recommended product id and score of similarity
        """
        ds = pd.read_csv(self.result_path)
        return ds.loc[ds['id'] == int(item_id)][:size]

    def post(self):
        self.content_based()
        return 1