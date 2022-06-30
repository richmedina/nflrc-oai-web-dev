from django import template

register = template.Library()

def metaprint(metaval, arg):
    """Returns a displayable version of a metadata field where input 
    strings have the delimiting period removed."""
    s = metaval.split(arg)
    return ' '.join(metaval.split(arg))

def dlookup(data, key):
    """Returns a value at key in data."""
    try:
    	return data[key][0]
    except:
    	return ''

register.filter('metaprint', metaprint)
register.filter('dlookup', dlookup)