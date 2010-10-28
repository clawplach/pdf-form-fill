============
pdf-form-fill	
============

A Django app that maps a model's fields and methods to fields in a PDF form, think of it as mail merge but with a PDF as a template.  Useful when you are only allowed to use predefined forms in a project for output.

Installation
============

 * Python 2.6
 * Django 1.0+
 * pdftk (PDF tool kit)

Setting up
==========

Add to an existing project in settings.INSTALLED_APPS.
Execute manager syncdb to created the necesary database tables.


Usage
==========

Design the model to PDF field mapping using the admin interface.
Call generate_form() to produce a resulting PDF file merged from the original PDF form and the model's data.


License
=======
pdf-form-fill is licensed under the terms of the GNU License version 3, see the included LICENSE file.
