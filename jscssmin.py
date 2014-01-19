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
    'config': "ceco.settings",
    'path': ("/home/transweb/apps_wsgi/ceco",
             #"mode paths....",
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
                           'full': '',
                           'cssmin': 'static/css/ceco.min.css'
                           },
               },
    }

#-------------------------------------------------------------------------
import urllib2, urllib
import os
import sys
import mimetypes
import random
import string


__author__ = 'Gustavo Vargas <xgvargas@gmail.com>'
__all__ = [
    'jsMin',
    'cssMin',
    'jpgMin',
    'pngMin'
]


if merger.get('config'): #only imports django if we have a config file defined
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


def _read(file, mode='r'):
    """
    Read entire file content.
    """
    with open(file, mode) as fh:
        return fh.read()


def _save(file, data, mode='w+'):
    """
    Write all data to created file. Also overwrite previous file.
    """
    with open(file, mode) as fh:
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


def jpgMin(file, force=False):
    """
    Try to optimise a JPG file.
    
    The original will be saved at the same place with '.original' appended to its name.
    
    Once a .original exists the function will ignore this file unless force is True.
    """
    if not os.path.isfile(file+'.original') or force:
        data = _read(file, 'rb')
        _save(file+'.original', data, 'w+b')
        print 'Optmising JPG {} - {:.2f}kB'.format(file, len(data)/1024.0),
        url = 'http://jpgoptimiser.com/optimise'
        parts, headers = encode_multipart({}, {'input': {'filename': 'wherever.jpg', 'content': data}})
        req = urllib2.Request(url, data=parts, headers=headers)
        try:
            f = urllib2.urlopen(req)
            response = f.read()
            f.close()
            print ' - {:.2f} - {:.1f}%'.format(len(response)/1024.0, 100.0*len(response)/len(data))
            _save(file, response, 'w+b')
        except:
            print 'Oops!! Failed :('
            return 1
    else:
        print 'Ignoring file: {}'.format(file)
    return 0
    
    
def pngMin(file, force=False):
    """
    Try to optimise a PNG file.
    
    The original will be saved at the same place with '.original' appended to its name.
    
    Once a .original exists the function will ignore this file unless force is True.
    """
    if not os.path.isfile(file+'.original') or force:
        data = _read(file, 'rb')
        _save(file+'.original', data, 'w+b')
        print 'Crushing PNG {} - {:.2f}kB'.format(file, len(data)/1024.0),
        url = 'http://pngcrush.com/crush'
        parts, headers = encode_multipart({}, {'input': {'filename': 'wherever.jpg', 'content': data}})
        req = urllib2.Request(url, data=parts, headers=headers)
        try:
            f = urllib2.urlopen(req)
            response = f.read()
            f.close()
            print ' - {:.2f}kB - {:.1f}%'.format(len(response)/1024.0, 100.0*len(response)/len(data))
            _save(file, response, 'w+b')
        except:
            print 'Oops!! Failed :('
            return 1
    else:
        print 'Ignoring file: {}'.format(file)
    return 0


#this codes cames from: http://code.activestate.com/recipes/578668-encode-multipart-form-data-for-uploading-files-via/
def encode_multipart(fields, files, boundary=None):
    r"""Encode dict of form fields and dict of files as multipart/form-data.
    Return tuple of (body_string, headers_dict). Each value in files is a dict
    with required keys 'filename' and 'content', and optional 'mimetype' (if
    not specified, tries to guess mime type or uses 'application/octet-stream').

    >>> body, headers = encode_multipart({'FIELD': 'VALUE'},
    ...                                  {'FILE': {'filename': 'F.TXT', 'content': 'CONTENT'}},
    ...                                  boundary='BOUNDARY')
    >>> print('\n'.join(repr(l) for l in body.split('\r\n')))
    '--BOUNDARY'
    'Content-Disposition: form-data; name="FIELD"'
    ''
    'VALUE'
    '--BOUNDARY'
    'Content-Disposition: form-data; name="FILE"; filename="F.TXT"'
    'Content-Type: text/plain'
    ''
    'CONTENT'
    '--BOUNDARY--'
    ''
    >>> print(sorted(headers.items()))
    [('Content-Length', '193'), ('Content-Type', 'multipart/form-data; boundary=BOUNDARY')]
    >>> len(body)
    193
    """
    def escape_quote(s):
        return s.replace('"', '\\"')

    if boundary is None:
        boundary = ''.join(random.choice(string.digits + string.ascii_letters) for i in range(30))
    lines = []

    for name, value in fields.items():
        lines.extend((
            '--{0}'.format(boundary),
            'Content-Disposition: form-data; name="{0}"'.format(escape_quote(name)),
            '',
            str(value),
        ))

    for name, value in files.items():
        filename = value['filename']
        if 'mimetype' in value:
            mimetype = value['mimetype']
        else:
            mimetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        lines.extend((
            '--{0}'.format(boundary),
            'Content-Disposition: form-data; name="{0}"; filename="{1}"'.format(
                    escape_quote(name), escape_quote(filename)),
            'Content-Type: {0}'.format(mimetype),
            '',
            value['content'],
        ))

    lines.extend((
        '--{0}--'.format(boundary),
        '',
    ))
    body = '\r\n'.join(lines)

    headers = {
        'Content-Type': 'multipart/form-data; boundary={0}'.format(boundary),
        'Content-Length': str(len(body)),
    }

    return (body, headers)

if __name__ == '__main__':
    import doctest
    doctest.testmod()


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
    if len(sys.argv) > 2:
        print """Error! Use jscssmin.py [--images|--images-full]"""
        exit(1)

    img, imgfull = False, False
    if len(sys.argv) == 2:
        if sys.argv[1] == '--images': img = True
        elif sys.argv[1] == '--images-full': img, imgfull = True, True
        else:
            print """Error! Use jscssmin.py [--images|--images-full]"""
            exit(1)
    
    for k, j in merger['blocks'].items():
        print '\nProcessing block: {}'.format(k)
        process(j)
    
    if img:
        print '\nProcessing images'
        for root, dirs, files in os.walk(os.getcwd()):
            for f in files:
                if f.endswith('.jpg'):
                    jpgMin(os.path.join(root, f), imgfull)
                elif f.endswith('.png'):
                    pngMin(os.path.join(root, f), imgfull)
