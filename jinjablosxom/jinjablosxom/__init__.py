#######################################################################
# Jinja2 pyblosxom renderer.
#
# Massively inspired by Sebastian Spaeth's Jinja2 renderer (and even
# borrows some code) but mostly reimplemented by Chris Webber.
#
# Copyright (c) 2010-2011 Sebastian Spaeth, Christopher Allan Webber
#
# PyBlosxom (and this jinja2 plugin) distributed under the MIT
# license.  See the file LICENSE for distribution details.
#######################################################################

__author__ = "Christopher Allan Webber / Sebastian Spaeth"
__version__ = "0.1"
__url__ = "http://dustycloud.org/"
__description__ = "Allows to configure jinja2 as py['renderer']."


from Pyblosxom.renderers.base import RendererBase
from Pyblosxom import tools
import jinja2, sys
import posixpath
import urllib


class Jinja2Renderer(RendererBase):
    """
    Jinja2 renderer.

    This is a fairly easy renderer to use.  It only has a couple of
    configuration options:

     - jinja2.template_dir: Optional, provides a directory full of
       Jinja2 templates.  If not provided, some defaults from this
       package are used.
     - jinja2.env: Optional, provide your entire own jinja2 template
       environment which you provide in your config.py.  Do this and
       you don't need jinja2.template_dir ;)
     - jinja2.flav_subdir: Subdirectory within your template directory
       within which the jinja2 flavors exist
    """

    def __init__(self, request, stdoutput=sys.stdout):
        RendererBase.__init__(self, request, stdoutput)
        self.config = request.config
        self.data = request.data
        self._request = request
        self.jinja_env = self._get_template_env()

    def get_context(self):
        """
        Returns a dict starting with standard filters, config
        information, then data information.  This allows vars
        to override each other correctly.  For example, plugins
        should be adding to the data dict which will override
        stuff in the config dict.

        Also tacks in the request because I like that kind of thing.

        XXX: Should we switch this over to something like:
          {'filters': tools.STANDARD_FILTERS,
           'config': self.config,
           'data': self.data,
           'request': self.request}
        instead?
        """
        parsevars = dict(tools.STANDARD_FILTERS)
        parsevars['request'] = self._request
        parsevars.update(self.config)
        parsevars.update(self.data)
        if isinstance(self._content, list):
            parsevars['content'] = self._content
        else:
            parsevars['content'] = [self._content]
        parsevars['urlencode'] = tools.urlencode_text
        parsevars['entry_templates'] = self.setup_entry_templates(
            parsevars['content'])
        return parsevars

    def render(self, header=1):
        # setup headers
        if header:
            if self._header:
                self.show_headers()
            else:
                self.add_header('Content-Type', 'text/html')
                self.show_headers()

        # get context
        context = self.get_context()

        # get base template
        template = self.get_template(
            self.data.get('flavour', 'html'),
            '__base')

        # render
        rendered = template.render(context).encode('utf-8')
        self.write(rendered)

    def setup_entry_templates(self, entries):
        """
        Produce a list of tuples of (entry, template)
        """
        entry_templates = []
        for entry in entries:
            if not entry:
                continue
            template = self.get_template(
                self.data.get('flavour', 'html'),
                entry.get('template_name', 'story'))
            entry_templates.append((entry, template))

        return entry_templates

    def _get_template_env(self):
        if 'jinja2.env' in self.config:
            return self.config['jinja2.env']
        elif 'jinja2.template_dir' in self.config:
            loader = jinja2.ChoiceLoader(
                [jinja2.FileSystemLoader(self.config['jinja2.template_dir']),
                 jinja2.PackageLoader('jinjablosxom', 'templates')])
        else:
            loader = jinja2.PackageLoader('jinjablosxom', 'templates')

        return jinja2.Environment(
            loader=loader, autoescape=True,
            extensions=['jinja2.ext.autoescape'])

    def get_template(self, flavour, template_name):
        flav_subdir = self.config.get('jinja2.flav_subdir', 'flavours')
        # not using os.path.join for windows users' sake :P
        template_path = posixpath.join(
            flav_subdir, "%s.flav" % flavour, template_name)

        return self.jinja_env.get_template(template_path)


def verify_installation(request):
    """
    Verifies the plugin installation checking for the required
    configuration properties.
    """
    config = request.getConfiguration()
    retval = 1
    if config.get('renderer','None') != 'jinjablosxom':
        # warn but don't fail if we are not configured to be used
        print ("WARNING: 'jinjablosxom' not configured in py['renderer']."
               " Plugin useless.")

    return retval


def cb_renderer(args):
    """ implements the renderer callback to provide the Jinja2 renderer.

        We only render if this plugin has been loaded AND if the user
        has configured py["renderer"] = "jinja2" in config.py.

        @param args: contains a key 'request' whose value is the Request().
        @type  args: dict
    """
    request = args['request']
    out = request.getConfiguration().get('stdoutput', sys.stdout)
    
    #only render if we have configured 'jinja2' as renderer
    if  request.getConfiguration().get('renderer', None) == 'jinjablosxom':
        return Jinja2Renderer(request, out)
