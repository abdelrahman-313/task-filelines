from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.renderers import JSONRenderer
from files.models import UploadedFile
from files.utils import random_line, read_lines
from files.renders import PlainTextRenderer, DictToXMLRenderer
from files.serializers import UploadedFileSerializer
from rest_framework import status
from drf_spectacular.utils import extend_schema
import random
import json
import dicttoxml


class FileUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        # Describe multipart explicitly (no serializer class here)
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "file": {"type": "string", "format": "binary"},
                },
                "required": ["file"],
            }
        },
        responses={
            201: {"type": "object", "properties": {"filename": {"type": "string"}}}
        },
        description="Upload a .txt file (multipart/form-data).",
    )
    def post(self, request):
        serializer = UploadedFileSerializer(data=request.data)
        if serializer.is_valid():
            obj = serializer.save()
            file_instance = obj[0] if isinstance(obj, list) else obj
            return Response(
                {"id": file_instance.id, "filename": file_instance.file.name},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RandomLineView(APIView):
    renderer_classes = [JSONRenderer, DictToXMLRenderer, PlainTextRenderer]

    @extend_schema(
        responses={
            200: {
                "application/json": {
                    "type": "object",
                    "properties": {"random_line": {"type": "string"}},
                    "required": ["random_line"],
                },
                "application/xml": {"type": "object"},
                "text/plain": {"type": "string"},
            }
        },
        description="Choose the Response content type; Swagger will send the Accept header.",
    )
    def get(self, request):
        file_obj = random.choice(UploadedFile.objects.all())
        data = random_line(file_obj)

        accept = request.GET.get("accept") or request.META.get(
            "HTTP_ACCEPT", "application/json"
        )
        if "text/plain" in accept:
            return HttpResponse(
                f"random_line:{data['line']}", content_type="text/plain"
            )

        elif "application/xml" in accept:
            xml = dicttoxml.dicttoxml(
                {"random_line": data["line"]}, custom_root="response", attr_type=False
            )
            return HttpResponse(xml, content_type="application/xml")

        elif "application/json" in accept:
            return HttpResponse(
                json.dumps({"random_line": data["line"]}),
                content_type="application/json",
            )

        return HttpResponse(json.dumps(data), content_type="application/json")


class RandomLineBackwardsView(APIView):
    def get(self, request):
        file_obj = random.choice(UploadedFile.objects.all())
        data = random_line(file_obj)
        return Response({"line_backwards": data["line"][::-1]})


class Longest100LinesView(APIView):
    def get(self, request):
        all_lines = []
        for f in UploadedFile.objects.all():
            for line in read_lines(f):
                all_lines.append(line.strip())
        longest = sorted(all_lines, key=len, reverse=True)[:100]
        return Response(longest)


class Longest20OfFileView(APIView):
    def get(self, request, file_id):
        f = UploadedFile.objects.get(id=file_id)
        lines = read_lines(f)
        longest = sorted(lines, key=len, reverse=True)[:20]
        return Response(longest)
