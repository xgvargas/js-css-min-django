#-*- coding: utf-8 -*-

"""
"""

#example of a merger dictionary for a django project:
#
#config key is optional but is necessary for template files
#if config is efined then path is mandatory. Can be blank otherwise.
#
#all files from static and the rendered version of template files under
#'my js' will be minified and saved to jsmin file.
#
#and all static files of 'my css' are going to be saved both full and
#minified version.
#
merger = {
    'config': "cecoe.settings",
    'path': ("/home/transweb/apps_wsgi/ceco",
             #"more paths....",
             ),
    'blocks': {'my js': {'static': ('static/js/ceco.js',
                                    'static/js/xvalidator.js',
                                    ),
                        'template': ('tasks/templates/tasks/tasks.js',
                                     'tasks/templates/tasks/cecomap.js',
                                     'message/templates/message/message.js',
                                     ),
                        'jsmin': 'static/js/ceco.min.js'
                        },
               'my css': {'static': ("tasks/static/tasks/css/fixtypeahead.css",
                                     "message/static/message/css/message.css"
                                     ),
                           'full': 'static/css/ceco.css',
                           'cssmin': 'static/css/ceco.min.css'
                           },
               },
    }


#-------------------------------------------------------------------------
import urllib2, urllib

if merger.get('config'): #only imports django if we have a config file defined
    import os
    import sys
    import re
    
    for p in merger['path']: sys.path.append(p)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", merger['config'])

    try:
        from django.template.loader import get_template_from_string
        from django.template.base import Context
        from django.utils.encoding import smart_str
        from django.conf import settings
    except:
        print 'Do you really have django well installed?'
        sys.exit(1)    


def _read(file):
    """
    Read entire file content.
    """
    with open(file, 'r') as fh:
        return fh.read()


def _save(file, data):
    """
    Write all data to created file. Also overwrite previous file.
    """
    with open(file, 'w+') as fh:
        fh.write(data)


def merge(obj):
    """
    Merge contents.
    
    It does a simply merge of all files defined under 'static' key.
    
    If you have JS or CSS file with embeded django tags like {% url ... %} or
    {% static ... %} you should declare them under 'template' key. This
    function will render them and append to the merged output.
    
    To use the render option you have to define both 'config' and 'path' on
    merger dictionary.
    """

    merge = ''

    for f in obj.get('static', []):
        print 'Merging: {}'. format(f)
        merge += _read(f)

    if merger.get('config'): #only process templates if we have a config
        for f in obj.get('template', []):
            print 'Merging template: {}'. format(f)
            t = _read(f)
            
            if settings.FORCE_SCRIPT_NAME:
                t = re.sub(r'\{%\s+url\b', settings.FORCE_SCRIPT_NAME+'{% url ', t)
                
            merge += smart_str(get_template_from_string(t).render(Context({})))
    
    return merge


def jsMin(data, file):
    """
    Minify JS data and saves to file.
    
    Data should be a string will whole JS content, and file will be
    overwrited if exists.
    """
    print 'Minifying JS... ',
    url = 'http://javascript-minifier.com/raw' #POST
    req = urllib2.Request(url, urllib.urlencode({'input': data}))
    try:
        f = urllib2.urlopen(req)
        response = f.read()
        f.close()
        print 'Final: {:.1f}%'.format(100.0*len(response)/len(data))
        print 'Saving: {} ({:.2f}kB)'.format(file, len(response)/1024.0)
        _save(file, response)
    except:
        print 'Oops!! Failed :('
        return 1
    return 0


def cssMin(data, file):
    """
    Minify CSS data and saves to file.
    
    Data should be a string will whole CSS content, and file will be
    overwrited if exists.
    """
    print 'Minifying CSS... ',
    url = 'http://cssminifier.com/raw' #POST
    req = urllib2.Request(url, urllib.urlencode({'input': data}))
    try:
        f = urllib2.urlopen(req)
        response = f.read()
        f.close()
        print 'Final: {:.1f}%'.format(100.0*len(response)/len(data))
        print 'Saving: {} ({:.2f}kB)'.format(file, len(response)/1024.0)
        _save(file, response)
    except:
        print 'Oops!! Failed :('
        return 1
    return 0


def process(obj):
    """
    Process each block of the merger object.
    """
    #merge all static and optional template files
    merged = merge(obj)

    #save the full file if name defined
    if obj.get('full'):
        print 'Saving: {} ({:.2f}kB)'.format(obj['full'], len(merged)/1024.0)
        _save(obj['full'], merged)
    else:
        print 'Full merged size: {:.2f}kB'.format(len(merged)/1024.0)
        
    #minify js and save to file
    if obj.get('jsmin'):
        jsMin(merged, obj['jsmin'])    

    #minify css and save to file
    if obj.get('cssmin'):
        cssMin(merged, obj['cssmin'])    


if __name__ == '__main__':
    for k, j in merger['blocks'].items():
        print '\nProcessing block: {}'.format(k)
        process(j)
    