from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services.sap_parser import SAPParserService
from emissions.models import Company

class SAPUploadView(APIView):
    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        company_id = request.data.get('company_id')
        if not company_id:
            company = Company.objects.first()
            if not company:
                company = Company.objects.create(name="Default Company")
            company_id = company.id

        try:
            parser = SAPParserService(file_obj, company_id)
            count = parser.process()
            return Response({"message": "File processed successfully", "rows_processed": count}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
