import io
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from PIL import Image, ImageOps
import pillow_heif

pillow_heif.register_heif_opener()

# Vercel serverless functions reject request bodies above 4.5 MB
MAX_BYTES = 4 * 1024 * 1024 + 400 * 1024


def to_jpeg_bytes(data, quality=90):
    with Image.open(io.BytesIO(data)) as image:
        exif = image.info.get("exif")
        # Bake the orientation into the pixels so the rotation is not lost
        image = ImageOps.exif_transpose(image)
        if image.mode != "RGB":
            image = image.convert("RGB")
        save_kwargs = {"format": "JPEG", "quality": quality}
        if exif:
            save_kwargs["exif"] = exif
        out = io.BytesIO()
        image.save(out, **save_kwargs)
        return out.getvalue()


class handler(BaseHTTPRequestHandler):
    def _send(self, status, body, content_type="text/plain; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            return self._send(400, b"No image uploaded")
        if length > MAX_BYTES:
            return self._send(413, b"Image is too large (max 4 MB)")

        params = parse_qs(urlparse(self.path).query)
        try:
            quality = min(100, max(1, int(params.get("quality", ["90"])[0])))
        except ValueError:
            return self._send(400, b"Invalid quality")

        try:
            jpeg = to_jpeg_bytes(self.rfile.read(length), quality)
        except Exception:
            return self._send(415, b"Could not read this file as an image")
        self._send(200, jpeg, "image/jpeg")
