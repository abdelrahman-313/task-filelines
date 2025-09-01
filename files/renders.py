from rest_framework.renderers import BaseRenderer
import dicttoxml


class PlainTextRenderer(BaseRenderer):
    media_type = "text/plain"
    format = "txt"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if isinstance(data, dict):
            return "\n".join(f"{k}: {v}" for k, v in data.items())
        return str(data)


class DictToXMLRenderer(BaseRenderer):
    media_type = "application/xml"
    format = "xml"
    charset = "utf-8"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        xml = dicttoxml.dicttoxml(data, custom_root="response", attr_type=False)
        return xml  # dicttoxml already returns bytes
