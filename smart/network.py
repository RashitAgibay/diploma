import os
import pandas as pd
from django.contrib.sites import requests

path = str(os.getcwdb().decode("utf-8").replace('\\', '/'))


def get_text(url: str, encoding='utf-8', to_lower=True):
    """

    Args:
        url: Url or Filename, must be string
        encoding: Encoding of Document default utf-8
        to_lower: convert content to lower, Boolean

    Returns:
        Str: content of document
    """
    if url.startswith('http'):
        request = requests.get(url)
        if not request.ok:
            request.raise_for_status()
        return request.text.lower() if to_lower else request.text
    elif os.path.exists(url):
        with open(url, encoding=encoding) as file:
            return file.read().lower() if to_lower else file.read()
    else:
        raise Exception('parameter [url] can be either URL or a filename')


#  <<=============================== Start Data Processing ===============================>>

# stop words for russian language
def get_stopwords():
    """

    Returns:
        Returns stopwords of Russian language
    """
    stopwords = get_text('smart/data/stopwords.txt').splitlines()
    return stopwords


def get_dataset():
    """
    Action:
        Prepare data for building a model
    Returns:
        DataFrame: [id,description]
    """
    # import Products data as DataFrame
    data_path = path+"/smart/data/products.csv"
    products = pd.read_csv(data_path)

    # clear data from not usable data
    products = products[
        ["id", "title", "mini_description", "category_id",
         "description", "manufacturer", "protection", "warranty"]  # todo Integrate with store_data( when
        # store registration must write which columns matter
    ]

    # merge columns for use in content-based model as in description column
    products['description'] = products[products.columns[1:]].apply(
        lambda x: ','.join(x.dropna().astype(str)),
        axis=1
    )

    # remove not usable columns from ds
    ds = products.drop(columns=["title", "mini_description", "category_id", "manufacturer", "protection", "warranty"])
    return ds

#  <<=============================== End Data Processing ===============================>>


