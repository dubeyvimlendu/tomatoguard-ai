import io

from PIL import Image, ImageOps, UnidentifiedImageError

from ..config import settings


class InferenceError(Exception):
    def __init__(self, status: int, message: str):
        self.status, self.message = status, message


def read_and_validate(filename: str | None, content_type: str | None, data: bytes) -> Image.Image:
    """Validates and decodes fully in memory: no upload is ever written to disk,
    so there are no temp files to clean up and the client filename is never used."""
    name = (filename or "").lower()
    ext = name[name.rfind("."):] if "." in name else ""
    if ext not in settings.allowed_ext or content_type not in settings.allowed_mime:
        raise InferenceError(415, "Unsupported file type. Please upload a JPG, PNG or WebP image.")
    if not data:
        raise InferenceError(400, "The uploaded file is empty.")
    if len(data) > settings.max_upload_bytes:
        raise InferenceError(413, f"Image is too large. Maximum size is {settings.max_upload_bytes // 1048576} MB.")
    try:
        Image.open(io.BytesIO(data)).verify()
        img = Image.open(io.BytesIO(data))
        if img.width * img.height > settings.max_pixels:
            raise InferenceError(413, "Image resolution is too high. Please use a smaller photo.")
        return ImageOps.exif_transpose(img).convert("RGB")
    except InferenceError:
        raise
    except (UnidentifiedImageError, OSError, ValueError, SyntaxError):
        raise InferenceError(400, "This image could not be read. It may be corrupted.")
