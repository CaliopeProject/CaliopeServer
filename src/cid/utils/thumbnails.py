import Image
import base64
import StringIO
from wand.image import Image as WandImage


def _open_image(filename):
    try:
        im = Image.open(filename)
    except IOError, e:
        im = None
    return im


def get_thumbnail_size(height, width, max_height, max_width):
    if (width / max_width) > (height / max_height):
        s = float(max_height) / float(height)
        tw = int(float(width) * s)
        th = int(float(height) * s)
    else:
        s = float(max_width) / float(width)
        tw = int(float(width) * s)
        th = int(float(height) * s)
    return tw, th


def pil_make_thumbnail(im, max_height, max_width):
    width = im.size[0]
    height = im.size[1]
    tw, th = get_thumbnail_size(height, width, max_height, max_width)

    return im.resize((tw, th), Image.ANTIALIAS)


def _pdf_thumbnail(filename):
    img = WandImage(filename=filename + '[0]')
    tw, th = get_thumbnail_size(img.height, img.width, 50, 50)
    img.resize(tw, th)
    rawData = img.make_blob('jpeg')
    return base64.b64encode(rawData)


def _image_thumbnail(filename):
    im = _open_image(filename)

    if im:
        width = im.size[0]
        height = im.size[1]

        im5 = pil_make_thumbnail(im, 50, 50)

        io = StringIO.StringIO()
        im5.save(io, 'jpeg')
        rawData = io.getvalue()

        return base64.b64encode(rawData)
    return None


def get_thumbnail(filename, field_name='value', mimetype=None):
    if 'pdf' in mimetype:
        rv = {field_name: _pdf_thumbnail(filename)}
    else:
        rv = {field_name: _image_thumbnail(filename)}
    return rv
