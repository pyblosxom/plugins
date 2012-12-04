# Florian Bäuerle <florian.bae@gmail.com>
# fubar.ath.cx
# License: CC-BY-SA
# Tested and working on Python 2.7.3
# Installation: move into plugins directory and add "breadcrumbs" to py["load_plugins"]
# add it to your flavour with $(breadcrumbs)
"""
	Configuration in config.py
	py["breadcrumb_item"]: %(url)s and %(item)s
	py["breadcrumb_sep"]: Separator between crumbs
	py["breadcrumb_first"]: Title of first breadcrumb
	py["breadcrumb_labels"]: Labels for other plugins, like tags.
	example for breadcrumb_labels:
		{'pages' : '1,',
		 'tag'   : '0,Tag: '}
		With that dict, you suppress breadcrumbs for either the pages-
		and the tags-Plugin. The 0 or 1 in the dict tells the Plugin to
		use and entry-Title for the breadcrumb, when available.
		If only one Article is tagged with a certain keyword, you may
		not want to show this Articles title as Breadcrum, so you
		suppress the title with the 0.
		The Number is followed by a comma and the desired Label.
"""

__author__ = "Florian Bäuerle"
__email__ = "florian.bae@gmail.com"
__version__ = "2012-05-27"
__url__ = "http://fubar.ath.cx/"
__description__ = "Breadcrumb navigation"
__category__ = "navigation"
__license__ = "CC-BY-SA"
__registrytags__ = "1.5"


def verify_installation(request):
    # This needs no verification.
    return True

def cb_head(args):
    req = args["request"]
    entry = args["entry"]

    data = req.get_data()
    config = req.get_configuration()
 
    path = config.get("base_url")

    from Pyblosxom import tools
    
    ## Fallback if not configured
    BREADCRUMB_ITEM = '<a href="%(url)s">%(item)s</a>'
    BREADCRUMB_SEP  = ' &gt; '
    BREADCRUMB_FIRST = 'Home'
    BREADCRUMB_LABELS  = {'' : ''}
    
    ## Create the first element
    entry["breadcrumbs"] = config.get("breadcrumb_item", BREADCRUMB_ITEM) % {"item": config.get("breadcrumb_first", BREADCRUMB_FIRST), "url": path }
    url = ""

    ## Get the labels for URLs
    labels = config.get("breadcrumb_labels", BREADCRUMB_LABELS);
    
    gap = False
    # Walk through the Path from pi_bl
    for item in data["pi_bl"].split("/"):
        # We only add a breadcrumb if there really is an item
        if (item != "index."+data["flavour"]) and (len(item)>0):# and (item != config.get("pages_trigger","")) and (item != "tag"):
        
            # Create path
            path += "/" + tools.urlencode_text(item)
            
            # Generate URL for the item
            if item[-len(data["flavour"])-1:] == "."+data["flavour"]:
                url = path
                # Remove .flav from item
                item = item[:-len(data["flavour"])-1]
            else:
                url = path + "/index."+data["flavour"]

            # Check for labels and extract title
            if item in labels:
                # We dont want a breadcrumb for this one
                gap = True
            else:
                import string
                # If we got a page with a single entry, get the title of it instead of the Filename                
                if (data["pi_bl"].split("/")[-1][:-len(data["flavour"])-1] == item):
                    title = True
                    # Let's go through labels and see if we actually want a title
                    label = ""
                    for x in labels:
                        if string.find(path, '/'+x+'/') != -1:
                            # Don't forget the label, if there is one
                            if labels[x][:1] == "0":
                                title = False
                                item = labels[x][2:] + item
                            else:
                                label = labels[x][2:]
                        
                    if title:
                        # Let's try to get the title of this page
                        entry_list = data.get("entry_list", [])
                        if len(entry_list) == 1:
                            item = label + entry_list[0].get("title",item)

            # And add that breadcrumb
            if not gap:
                entry["breadcrumbs"] += config.get("breadcrumb_sep", BREADCRUMB_SEP)
                entry["breadcrumbs"] += config.get("breadcrumb_item", BREADCRUMB_ITEM) % {"item": item, "url": url}

            gap = False

    return args
