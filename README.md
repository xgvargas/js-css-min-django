js-css-min-django
=================

This is a python script for automated merge and minify of JS and CSS files.

Optionally it can parse django template tags embeded into css and js files.

And, if you have [lesscpy](https://github.com/lesscpy/lesscpy) installed you can compiled .LESS to .CSS defore merging.

Example with a django project
-----------------------------

During development I simply use django tags like *{% url ... %}* and *{% static ... %}* on my .js and .css files to define dynamic url to views and images of my project. At this point the .js and .css are placed into the templates directory of my app so I can *{% include ... %}* it to my .html templates and have the tags rendered to final urls. Of course the js and css will appear inline with the HTML content. For development I think this is fine.

On deploy you usually want all your javascript and styling to be in a single external file.

Here is how this script can help you with that:

On my base.html template I usually have something like this:

```html
<head>
...
<!-- css -->
{% if debug %}
  <link href="{% static 'tasks/css/fixtypeahead.css' %}" rel="stylesheet">
  <link rel="stylesheet/less" type="text/css" href="{% static 'message/css/message.less' %}" />
  <link rel="stylesheet/less" type="text/css" href="{% static 'tasks/css/tasks.less' %}" />
  <link rel="stylesheet/less" type="text/css" href="{% static 'tasks/css/compactform.less' %}" />
{% else %}
  <link href="{% static 'tasks/css/compactform.css' %}" rel="stylesheet">
  <link href="{% static 'css/mydeploycss.min.css' %}" rel="stylesheet">
{% endif %}
{% block extracss %}{% endblock %}

<!-- js -->
{% if debug %}
  <script type="text/javascript" src="{% static 'js/less-1.6.2.min.js' %}"></script> <!-- while debugging less -->
  <script src="{% static 'js/code1.js' %}"></script>
  <script src="{% static 'js/code2.js' %}"></script>
  <script>
    <!-- js bellow contain django tags inside -->
    {% include 'tasks/code3template.js' %}
    {% include 'tasks/codentemplate.js' %}
    {% include 'message/moretemplatecode.js' %}
  </script>
{% else %}
  <script src="{% static 'js/deploycode.min.js' %}"></script>
{% endif %}
{% block extrajs %}{% endblock %}
...
</head>
```

Then simply put this script on the same directory as manager.py. Edit the script to adjust your paths to settings.py and to every JS and CSS you whant to merge/minify. Like:

```python
merger = {
    'config': "myapp.settings",
    'path': ("/home/username/apps_wsgi/myapp",
             #"more paths....",
             ),
    'blocks': {'my js': {'static': ('static/js/code1.js',
                                    'static/js/code2.js',
                                    ),
                         'template': ('tasks/templates/tasks/code3template.js',
                                      'tasks/templates/tasks/codentemplate.js',
                                      'message/templates/message/moretemplatecode.js',
                                      ),
                         #all static and rendered template JS will be merged, minified and saved to:
                         'jsmin': 'static/js/deploycode.min.js'
                         },

               'my css': {'static': ("tasks/static/tasks/css/fixtypeahead.css",
                                     ),
                          'less': ("message/static/message/css/message.less",
                                   "tasks/static/tasks/css/tasks.less"
                                   ),
                          #the static css and the css compiled from less files are merged, minified and saved to:
                          'cssmin': 'static/css/mydeploycss.min.css'
                          },

               'compact': {'less': ("tasks/static/tasks/css/compactform.less",
                                    ),
                           #the single less is compiled to css and saved as is to:
                           'full': 'tasks/static/tasks/css/compactform.css'
                           },
               },
    }
```

Here we define a path to the django project and the settings.py file to use while rendering the template tags. *You only need to define those if you have tags inside .js or .css, if you don't then simply ignore both*.

In this case we have two blocks, *my js* and *my css*.

For the first block all five javascript files are going to be merged, minified and saved to a single *cecoe.min.js* file. (Yes, the 3 files under *template* will be rendered before merge)

For the second block we have two .css files saved both in a single full merged file and also a mini version of it.

Once you update the work copy of your django project on your server all you have to do is:

```bash
$python jscssmin.py
Processing block: my css
Merging: tasks/static/tasks/css/fixtypeahead.css
Merging: message/static/message/css/message.css
Saving: static/css/ceco.css (2.28kB)
Minifying CSS...  Final: 73.7%
Saving: static/css/ceco.min.css (1.68kB)

Processing block: my js
Merging: static/js/ceco.js
Merging: static/js/xvalidator.js
Merging template: tasks/templates/tasks/tasks.js
Merging template: tasks/templates/tasks/cecomap.js
Merging template: message/templates/message/message.js
Saving: static.js.ceco.js (29.17kB)
Minifying JS...  Final: 50.3%
Saving: static.js.ceco.min.js (14.67kB)

$python manage.py collectstatic
$touch /path/to/yourwsgi.wsgi
```

Ok, this can change on your server but that's the overall idea...

Also you can use the option *--images* to optimise **all** *.PNG* and *.JPG* present on the directory tree starting where you executed this script (usualy your django project root). Like:

```bash
$python jscssmin.py --images
```

This will save a copy of all original images with *".original"* appended to its name and a smaller (hopefully), version will be saved with the original name. This script will ignore every file that already have a *.original* version present. To force this script to process every single file again use the option *--images-full*.

Non django project
------------------

No secret: simply edit this script to remove the *config*, and define all static files you want to merge/minify. Without a defined *config* all files under *templates* are going to be ignorated.

Using as a minifier module
--------------------------

In another python script:
```python
import  jscssmin

#minify JS from text to file
fulljstext = '<script>full code....</script>'
jscssmin.jsMin(fulljstext, 'path/to/min/code.js')

#minify CSS from text to file
fullcsstext = '<style>full styles...</style>'
jscssmin.cssMin(fullcsstext, 'path/to/min/style.css')

#minify a JPG image
jscssmin.jpgMin('path/to/image.jpg')

#minify a PNG image
jscssmin.pngMin('path/to/image.png')
```

All four functions used above are only helper to call some online minifer api. See below. This script does not minify JS or CSS by itself, so you need to be online to execute this with success.

Minifier
--------

This script uses some online api provided by [@andychilton] for all minify action:
+ http://javascript-minifier.com
+ http://cssminifier.com
+ http://pngcrush.com
+ http://jpgoptimiser.com

[@andychilton]: http://twitter.com/andychilton
