# files/serializers.py
from rest_framework import serializers
from .models import UploadedFile


class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = ["file"]

    def validate_file(self, value):
        # Ensure file is a text file
        if not value.name.endswith(".txt"):
            raise serializers.ValidationError("Only .txt files are allowed.")
        if getattr(value, "content_type", None) and not value.content_type.startswith(
            "text/plain"
        ):
            raise serializers.ValidationError("Only text/plain files are allowed.")
        return value
