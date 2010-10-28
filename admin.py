from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from models import Form, FormFieldMapping, FormField, MappingProperty 

class MappingPropertyInline(admin.StackedInline):
    model = MappingProperty
    extra = 1
    classes = ('collapse-open',)
    allow_add = True

class FormFieldMappingAdmin(admin.ModelAdmin):
    inlines = [
        MappingPropertyInline,
    ]

admin.site.register(Form)
admin.site.register(FormFieldMapping, FormFieldMappingAdmin)
