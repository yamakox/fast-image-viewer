from rest_framework import renderers
from pathlib import Path

class _ImageRenderer(renderers.BaseRenderer):
    charset = None
    render_style = 'binary'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data

# 画像のMIMEタイプについては、以下を参照。
# https://developer.mozilla.org/ja/docs/Web/HTTP/Guides/MIME_types
# https://www.iana.org/assignments/media-types/media-types.xhtml#image

class AVIFRenderer(_ImageRenderer):
    media_type = 'image/avif'
    format = 'avif'

class GIFRenderer(_ImageRenderer):
    media_type = 'image/gif'
    format = 'gif'

class HEICRenderer(_ImageRenderer):
    media_type = 'image/heic'
    format = 'heic'

class JPEGRenderer(_ImageRenderer):
    media_type = 'image/jpeg'
    format = 'jpg'

class PNGRenderer(_ImageRenderer):
    media_type = 'image/png'
    format = 'png'

class WEBPRenderer(_ImageRenderer):
    media_type = 'image/webp'
    format = 'webp'


IMAGE_SUFFIXES = {
    '.avif': AVIFRenderer,
    '.gif': GIFRenderer,
    '.heic': HEICRenderer,
    '.jpg': JPEGRenderer, 
    '.jpeg': JPEGRenderer, 
    '.png': PNGRenderer, 
    '.webp': WEBPRenderer, 
}


def find_renderer(filePath: Path) -> renderers.BaseRenderer|None:
    suffix = filePath.suffix.lower()
    return IMAGE_SUFFIXES.get(suffix)
