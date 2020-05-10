from project.custom_functions import api2_response
from rest_framework.views import APIView
from rest_framework import status
from .network import get_stopwords, get_dataset
from .recommendation import Recommendations


class SmartView(APIView):
    """

    """
    status_code = status.HTTP_200_OK
    detail = "Action created"
    data = {}
    safe = True

    def post(self, request, action=""):
        """

        Args:
            request:
            action:

        Returns:

        """
        ds = get_dataset()
        stopwords = get_stopwords()
        rec = Recommendations(ds, stopwords)
        rec.post()
        return api2_response(self)

    def get(self, request, item_id=10):
        """

        Args:
            request:
            item_id:

        Returns:

        """
        self.data = {}
        results = Recommendations().get(item_id, 4)
        for index, row in results.iterrows():
            if row['score'] == 1.0:
                continue
            self.data[int(row['rec_id'])] = row['score']
        return api2_response(self)
