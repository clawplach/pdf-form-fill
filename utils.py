import codecs
import os
import tempfile
import sys
import subprocess
import types

from models import Form, FormFieldMapping
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.translation import ugettext_lazy as _

#From - http://mousebender.wordpress.com/2006/11/10/recursive-getattrsetattr/
def return_attrib(obj, attrib):
    """Makes accessing an object's attributes or methods much simpler
    """
    
    try:
        result = reduce(getattr, attrib.split("."), obj)
        if isinstance(result, types.MethodType):
            return result()
        else:
            return result
    except:
        return _(u"Field error: %s" % attrib)

def generate_form(source_obj, form_id):
    try:
        form = Form.objects.get(id=form_id)
    except Form.DoesNotExist:
        return None
    fdf_filepath = tempfile.mkstemp()
    
    header = "<?xml version='1.0' encoding='UTF-8'?>\n";
    header += "<xfdf xmlns='http://ns.adobe.com/xfdf/' xml:space='preserve'>\n";
    header += "<fields>\n";		

    footer = "</fields>";
    #footer += "<f href='".$pdf_file."'/>";
    footer += "</xfdf>";

    body_template = "<field name='%s'>\n<value>%s</value>\n</field>\n";

    fdf_f = codecs.open(fdf_filepath, "w", "utf-8")
    fdf_f.write(header)
    
    try:
        fieldmap = FormFieldMapping.objects.get(form = form)
        for mapping in fieldmap.mappings.all():
            form_field = mapping.mappingproperty_set.get().form_field.fieldname
            source_field = mapping.mappingproperty_set.get().source_field
            operand = mapping.mappingproperty_set.get().operand
            argument = mapping.mappingproperty_set.get().argument
            if operand not in ['CONCAT', 'FIXED']:
                result = return_attrib(source_obj, source_field)
                #TODO: M2M
                #p.child_permit_content_object.project_type.values_list('name',flat=True)

            if operand == 'SPLIT' and result:
                #The split operand
                delimiter = argument.split(',')[0]
                arg_num = argument.split(',')[1]
                result = result.split(delimiter)[int(arg_num)]
            elif operand == 'CONCAT' and result:
                #The concatenate operand
                result = ''
                for field in argument.split(','):
                    result += return_attrib(source_obj, field)
                    #TODO: delimiter?
                    #'.'.join([x for x in [i for i in a.split(',')]])
            elif operand == 'FIXED':
                #The fixed value operand
                result = argument
                
            if result:
                fdf_f.write(body_template % (form_field, unicode(result)))

    except FormFieldMapping.DoesNotExist:
        pass
            
    fdf_f.write(footer)
    fdf_f.close()
    
    newform_filepath = tempfile.mktemp()
    command_line = "pdftk %(pdf_form)s fill_form %(form_fdf)s output %(new_form)s" % {'pdf_form':form.source_filename.path, 'form_fdf':fdf_filepath, 'new_form':newform_filepath}

    try:
        retcode = subprocess.call(command_line, shell=True)
        if retcode < 0:
            return None
    except OSError, e:
        return None
    
    result = {
        'form_path' : newform_filepath,
        'form_name' : form.name,
    }
    
    return result
