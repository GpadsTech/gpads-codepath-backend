from rest_framework.response import Response
from rest_framework.views import APIView

from app.config.dependencies import get_container


class Controller(APIView):
    @property
    def services(self):
        return get_container()

    @staticmethod
    def ok(data, status=200):
        return Response({"success": True, "data": data}, status=status)
