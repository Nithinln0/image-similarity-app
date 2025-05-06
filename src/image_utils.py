from PIL import Image
from io import BytesIO

def image_to_bytes(img_file):
    return img_file.getvalue()

def bytes_to_image(blob):
    return Image.open(BytesIO(blob))
