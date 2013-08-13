import Image
import base64
import StringIO 

def _open_image(filename):
    try:
        im = Image.open(filename)
    except IOError, e:
        im = None
    return im

def make_thumbnail(im, max_height, max_width):
    width = im.size[0] 
    height = im.size[1] 
    if (width/max_width) > (height/max_height):
        s = float(max_height)/float(height)
        tw = int(float(width)*s)
        th = int(float(height)*s)
    else:
        s = float(max_width)/float(width)
        tw = int(float(width)*s)
        th = int(float(height)*s)
    return im.resize((tw, th), Image.ANTIALIAS)

def get_thumbnail(filename):
    rv = {'data':None}
    im = _open_image(filename)
   
    if im:
        width = im.size[0] 
        height = im.size[1] 
        
        im5 = make_thumbnail(im,50,50)
        
        io=StringIO.StringIO() 
        im5.save(io,'jpeg')
        rawData = io.getvalue()
        
        encoded = base64.b64encode(rawData)
        rv = {'data':encoded} 
    return rv
