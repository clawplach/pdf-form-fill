import subprocess

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.utils.text import capfirst


class Form(models.Model):
    name = models.CharField(max_length=32, verbose_name=_(u'name'))
    title = models.CharField(max_length=64, verbose_name=_(u'title'))
    description = models.TextField(null=True, blank=True,
                                    verbose_name=_(u'description'))
    source_filename = models.FileField(upload_to='forms',
                                    verbose_name=_(u'source filename'))

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.title)

    def save(self, *args, **kwargs):
        """Open the PDF file, extract all the fields it contains and
        save them into the FormField model
        """

        super(Form, self).save(*args, **kwargs)
        
        p1 = subprocess.Popen(["pdftk", self.source_filename.path, 'dump_data_fields'],
                              stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["grep", "FieldName"], stdin=p1.stdout,
                              stdout=subprocess.PIPE)
        new_fields=[l.split(":")[1].strip() for l in p2.stdout]
        current_fields = FormField.objects.filter(form=self.id).values_list('fieldname', flat=True)
        to_delete = set(current_fields).difference(new_fields)
        to_add = set(new_fields).difference(current_fields)
        for field in to_delete:
            FormField.objects.get(fieldname=field).delete()
        for field in to_add:
            FormField(form=self, fieldname=field).save()
        
    class Meta:
        verbose_name = _(u"form")
        verbose_name_plural = _(u"forms")
        
        
class FormField(models.Model):
    """Represent the PDF fields that can be connected to a model's
    field or fields
    """

    form = models.ForeignKey(Form, verbose_name=_(u'form'))
    fieldname = models.CharField(max_length=72, verbose_name=_(u'field name'))
    
    def __unicode__(self):
        return "%s - %s" % (unicode(self.form), self.fieldname)

    class Meta:
        ordering = ['fieldname',]
        verbose_name = _(u"form field")
        verbose_name_plural = _(u"form fields")


class FormFieldMapping(models.Model):
    form = models.ForeignKey(Form, unique=True, verbose_name=_(u'form'))
    mappings = models.ManyToManyField(FormField, through='MappingProperty', verbose_name=_(u'mappings'))

    def __unicode__(self):
        return unicode(self.form)

    class Meta:
        verbose_name = _(u"form field mappings")
        verbose_name_plural = _(u"forms field mappings")

#TODO: Convert to dynamic encapsulated operands
#class Operand(models.Model):
    
class MappingProperty(models.Model):
    """Holds the details of a specific mapping of a model's fields to a
    specific field in the PDF form
    """
    
    OPERAND_CHOICES = (
        ('SPLIT', _(u"Split")),
        ('COCAT', _(u"Concatenate")),
        ('FIXED', _(u'Fixed')),
    )
    form_field = models.ForeignKey(FormField, verbose_name=_(u'form field'))
    form_field_mapping = models.ForeignKey(FormFieldMapping, verbose_name=_(u'form field mapping'))
    source_field = models.CharField(max_length = 72, null=True, blank=True,  verbose_name=_(u'source field')) 
    #operand = models.ForeignKey(Operands, null=True, blank=True)
    operand = models.CharField(blank = True, null = True, max_length = 10, choices = OPERAND_CHOICES, verbose_name = _(u'operand'))
    argument = models.CharField(max_length = 32, blank = True, null = True, verbose_name = _(u'argument'))
    
    def __unicode__(self):
        return "%s - %s" % (self.form_field, self.source_field)

    class Meta:
        verbose_name = _(u"mapping property")
        verbose_name_plural = _(u"mapping properties")
