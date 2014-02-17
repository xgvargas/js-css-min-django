js-css-min-django
=================

This is a python script for automated merge and minify of JS and CSS files.

Optionally it can parse django template tags embeded into css and js files.

And, if you have [lesscpy](https://github.com/lesscpy/lesscpy) installed, you can compiled .LESS to .CSS before merging.

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
  <!-- you need this only while debugging with less files -->
  <script type="text/javascript" src="{% static 'js/less-1.6.2.min.js' %}"></script>
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

Check out [less.js](https://github.com/less/less.js) for a less compiler at client side.

Create a file named *jscssmin.yaml* next to your manage.py (if using django, otherwire put this file in your root). Here's a example:

```yaml
---
config: myapp.settings
path:
    - /home/username/apps_wsgi/myapp
    #more path as you need
blocks:
    my js:
        static:
            - static/js/code1.js
            - static/js/code2.js
        template:
            - tasks/templates/tasks/code3template.js
            - tasks/templates/tasks/codentemplate.js
            - message/templates/message/moretemplatecode.js
        #all static and rendered template JS will be merged, minified and saved to:
        jsmin: static/js/deploycode.min.js
    my css:
        static:
            - tasks/static/tasks/css/fixtypeahead.css
        less:
            - message/static/message/css/message.less
            - tasks/static/tasks/css/tasks.less
        #the static css and the css compiled from less files are merged, minified and saved to:
        cssmin: static/css/mydeploycss.min.css
    compact:
        less:
            - tasks/static/tasks/css/compactform.less
        #the single less is compiled to css and saved as is to:
        full: tasks/static/tasks/css/compactform.css
...
```

Here we define a path to the django project and the settings.py file to use while rendering the template tags. *You only need to define those if you have tags inside .js or .css, if you don't then simply ignore both*.

In this case we have three blocks, *my js*, *my css* and *compact*.

For the first block all five javascript files are going to be merged, minified and saved to a single *deploycode.min.js* file. (Yes, the 3 files under *template* will be rendered before merge)

For the second block we have one .css and two .less files merged and minified.

In our least block the compactform.less file is compiled to CSS and saved as is to a CSS file.

Once you update/checkout the work copy of your django project on your server all you have to do is:

```bash
$jscssmin
Processing block: compact
Compiling LESS: tasks/static/tasks/css/compactform.less
Saving: tasks/static/tasks/css/compactform.css (0.17kB)

Processing block: my css
Merging: tasks/static/tasks/css/fixtypeahead.css
Compiling LESS: message/static/message/css/message.less
Compiling LESS: tasks/static/tasks/css/tasks.less
Full merged size: 2.66kB
Minifying CSS...  Final: 72.7%
Saving: static/css/mydeploycss.min.css (1.93kB)

Processing block: my js
Merging: static/js/code1.js
Merging: static/js/code2.js
Merging template: tasks/templates/tasks/code3template.js
Merging template: tasks/templates/tasks/codentemplate.js
Merging template: message/templates/message/moretemplatecode.js
Full merged size: 34.66kB
Minifying JS...  Final: 50.1%
Saving: static/js/deploycode.min.js (17.35kB)

$python manage.py collectstatic
$touch /path/to/yourwsgi.wsgi
```

Ok, this least step can change on your server, but that's the overall idea...

Also, you can use the option *--images* to optimise **all** *.PNG* and *.JPG* present on the directory tree starting where you executed this script (usualy your django project root). Like:

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

All four functions used above are only helpers to call some online minifer api. See below. **This script does not minify JS or CSS by itself, so you need to be online to execute this with success**.

Minifier
--------

This script uses some great online api provided by [@andychilton] for all minify action:
+ http://javascript-minifier.com
+ http://cssminifier.com
+ http://pngcrush.com
+ http://jpgoptimiser.com

[@andychilton]: http://twitter.com/andychilton
