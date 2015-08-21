"""
Human verification for the comments plugin.
Based on a idea and ref impl of Jesus Roncero Franco <jesus at roncero.org>.
Implemented as a pyblosxom plugin by Steven Armstrong <sa at c-area.ch>.

Creates a random number, generates an image of it, and stores the number
in the session.

If you make any changes to this plugin, please send a patch to 
<sa+pyblosxom at c-area dot ch> so I can incorporate them.
Thanks!


To install:
1) Put nospam.py in your plugin directory.
2) In config.py add nospam to py['load_plugins']
3) Add the following variables to config.py:
    py['nospam_font'] = '/path/to/truetype/font.ttf' # required, no default
    py['nospam_extension'] = '/nospam.png' # optional, this is the default


Add something like this to your comment-form.html template:
<label for="nospam">Secret Number:</label>
<img src="$base_url/nospam.png" alt="Secret Number Image" title="Type this number into the field on the right" />
<input name="nospam" id="nospam" type="text" value="" maxlength="5" style="width:5em" />


Dependecies:
    - My compatibility plugin if you're not using pyblosxom 1.2+.
    - My session plugin.
    - Python imaging library from http://www.pythonware.com/products/pil/


Revisions:
    $Log: nospam.py,v $
    Revision 1.2  2005/02/10 15:57:06  sar
    added cb_end callback to clean up

    Revision 1.1  2005/02/08 17:51:21  sar
    cvs server update

    Revision 1.5  2005/01/18 02:14:29  sar
    moved cgi stuff to the compatibility plugin

    Revision 1.4  2005/01/16 14:03:27  sar
    fixed typo in doctring

    Revision 1.3  2004/12/11 22:36:40  sar
    added comment_reject callback function,
    removed dependencies on my WSGI wrapper

    Revision 1.2  2004/12/04 16:21:19  sar
    removed dependencies on mod_python

    Revision 1.1  2004/11/27 23:54:58  sar
    created

$Id: nospam.py,v 1.2 2005/02/10 15:57:06 sar Exp $
"""
__author__ = "Steven Armstrong <sa at c-area dot ch>"
__version__ = "$Revision: 1.2 $ $Date: 2005/02/10 15:57:06 $"
__url__ = "http://www.c-area.ch/code/"
__description__ = "Human verification system for the comments plugin"
__license__ = "GPL 2+"


# Python imports
import sys
import os
import random

# PIL imports http://www.pythonware.com/products/pil/
import Image
import ImageDraw
import ImageFont
import ImageOps

# Pyblosxom imports
from Pyblosxom import tools

# parameters
_xstep = 5 
_ystep = 5 
_imageSize = (61,21)
_bgColor = (255,255,255) # White
_gridInk = (200,200,200)
_fontInk = (130,130,130)
_fontSize = 14
# set in cb_start callback
_fontPath = None

# the names of the fields used in the comment form
_form_fields = ["title", "author", "email", "url", "body"]


def verify_installation(request):
    config = request.getConfiguration()
    retval = 1
    
    try:
        import session
    except ImportError:
        print "Missing required plugin 'session.py'."
        retval = 0

    try:
        import compatibility
    except ImportError:
        print "If you're not running the WSGI version of Pyblosxom"
        print "you'll need the 'compatibility.py' plugin."

    if not config.has_key('nospam_font'):
        print "Missing required property: 'nospam_font'"
        print "This must be the absolute path to a truetype font."
        retval = 0

    if not config.has_key('nospam_extension'):
        print "Missing optional property: 'nospam_extension'"
        print "Using the default of '/nospam.png'"
    
    return retval


# This function is (c) Jesus Roncero Franco <jesus at roncero.org>.
def _generateImage(number):
    font = ImageFont.truetype(_fontPath, _fontSize)
    im = Image.new("RGB", _imageSize, _bgColor)
    draw = ImageDraw.Draw(im)
    
    xsize, ysize = im.size

    # Do we want the grid start at 0,0 or want some offset?
    x, y = 0,0
    
    draw.setink(_gridInk)
    while x <= xsize:
        draw.line(((x, 0), (x, ysize)))
        x = x + _xstep 
    while y <= ysize:
        draw.line(((0, y), (xsize, y)))
        y = y + _ystep 
    
    draw.setink(_fontInk)
    draw.text((10, 2), number, font=font)

    return im


def _writeImage(request):
    number = str(random.randrange(1,99999,1))

    session = request.getSession()
    session["nospam"] = number
    session.save()

    image = _generateImage(number)

    response = request.getResponse()
    response.addHeader('Content-Type', 'image/png')
    image.save(response, "PNG")


def _remember_comment(request):
    """
    Stores form fields in the data dict so they can be used to 
    refill the form in the template.
    
    @param request: pyblosxom request object
    @type request: L{Pyblosxom.pyblosxom.Request}
    """
    data = request.getData()
    form = request.getForm()
    for key in _form_fields:
        data["cmt_%s" % key] = (form.has_key(key) and [form[key].value] or [''])[0]


def _forget_comment(request):
    """
    Resets/forgets any stored form field values.
    
    @param request: pyblosxom request object
    @type request: L{Pyblosxom.pyblosxom.Request}
    """
    data = request.getData()
    for key in _form_fields:
        key = "cmt_%s" % key
        if key in data:
            del data[key]



#******************************
# Callbacks
#******************************

def cb_start(args):
    request = args['request']
    config = request.getConfiguration()
    global _fontPath
    _fontPath = config.get('nospam_font')


def cb_handle(args):
    request = args['request']
    http = request.getHttp()
    config = request.getConfiguration()
    ext = config.get("nospam_extension", "/nospam.png")
    if http['PATH_INFO'].endswith( ext ):
        # write the image to the output stream
        _writeImage(request)
        # return True to tell pyblosxom that the request has been taken care of
        return 1


def cb_comment_reject(args):
    """
    Checks if the the nospam number of the incomming request 
    matches the one stored in the session.
    Creates a template variable $cmt_nospam_error with a 
    error message if it didn't.
    
    Also creates the following template variables:
    $cmt_title, $cmt_author, $cmt_email, $cmt_url, $cmt_body
    which can be used to populate the form with the values
    provided by the user.

    @param args: a dict containing: pyblosxom request, comment dict 
    @type config: C{dict}
    @return: True if the comment should be rejected, False otherwise
    @rtype: C{bool}
    """
    request = args['request']
    session = request.getSession()
    form = request.getForm()
    data = request.getData()

    try:
        nospam = int(form["nospam"].value)
        sess_nospam = int(session["nospam"])
    except:
        nospam = 0
        sess_nospam = 1

    if nospam != sess_nospam:
        _remember_comment(request)
        data["cmt_nospam_error"] = "Secret number did not match."
        return True
    else:
        _forget_comment(request)
        if "cmt_nospam_error" in data:
            del data["cmt_nospam_error"]
        return False


def cb_end(args):
    request = args['request']
    data = request.getData()
    _forget_comment(request)
    if "cmt_nospam_error" in data:
        del data["cmt_nospam_error"]


