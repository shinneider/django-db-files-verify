import os
from operator import attrgetter
from pathlib import Path

import xlwt
from django.apps import apps
from django.conf import settings
from django.db.models.fields.reverse_related import ManyToManyRel, ManyToOneRel
from django.http import HttpResponse
from xlwt.Worksheet import Worksheet


class VerifyFilerFields(object):
    workbook = None
    file_fields = [
        # Django Filer
        'FilerImageField', 'FilerFolderField', 'FilerFileField',
        
        # Django Native
        'ImageField', 'FileField',  
    ]

    
    def __init__(self, *args, **kwargs):
        self.save_path = kwargs.get('save_path', settings.BASE_DIR + '/file_errors.xlsx')
        
        model = kwargs.get('model', None)
        
        if model:
            self.check_model(model)
        else:
            self.check_all_models()
        
        if self.workbook:
            self.return_xlsx()
            print('Errors saved into xlsx, in {0}'.format(self.save_path))
        else:
            print('All files in table exists in disk')
    
    def get_models(self):
        """ get all apps models """
        return apps.get_models()
    
    def check_all_models(self):
        """ 
            check database filer fields has not invalid file 
            ATENTION: this not check M2M tables!!! 
        """
        
        error = []
        for model in self.get_models():
            result = self._check_model(model, multiple=True)
            
            if not result[0]:
                error += result[1]
                
        if len(error) > 0:
            self.write_xlsx(error)
    
    def check_model(self, model):
        """ call to real check function, and output data"""
        result = self._check_model(model)
        if not result[0]:
            self.write_xlsx(error)
            
    def _check_model(self, model, multiple=False):
        """ check model function, verify model erros """
        fields = model._meta.get_fields()
        _objects = model.objects.all()
        
        _file_fields = [field.name for field in fields if self.check_file_field(field)]
        
        error = []
        if len(_file_fields) > 0:
            
            for object in _objects:
                result = self.verify_object(object, _file_fields, model.__name__)
                
                if not result[0]:
                    error += result[1]
            
        if len(error) < 1:
            return [True, ]
        else:
            return [False, error]
        
    def verify_object(self, object, fields, model_name):
        """ verify column is not null or blank and file exist"""
        
        model_fields = attrgetter(*fields)(object)
        fields_erros = []
        
        if isinstance(model_fields, tuple):
            for index, column in enumerate(model_fields):
                _result = self.verify_object_column(column, field[index], object.pk, model_name)
                fields_erros.append(_result) if _result is not None else ''
        else:
            _result = self.verify_object_column(model_fields, fields[0], object.pk, model_name)
            fields_erros.append(_result) if _result is not None else ''
        
        
        if len(fields_erros) > 0:   
            return [False, fields_erros]
        
        return [True,]
    
    def verify_object_column(self, column, field, object_pk, model_name):
        """ verify field in column exists """
        fields_erros = {}
        
        if column is not None or column != '':
            if not self.verify_file_exists(column.name):
                fields_erros['model'] = model_name
                fields_erros['pk'] = object_pk
                fields_erros['field'] = field
                fields_erros['file'] = column.name
        
        if len(fields_erros) > 0:
            return fields_erros
        else:
            return None
    
    def check_file_field(self, field):
        """ this check if is a file field"""
        if field.name != 'id' and not isinstance(field, (ManyToOneRel, ManyToManyRel)):
            
            field_type = self.get_field_type(field)
            
            if field_type in self.file_fields:
                return True
        
        return False
    
    def get_field_type(self, field):
        """ return db field type"""
        return field.get_internal_type()
    
    def verify_file_exists(self, name):
        """ check file exists in directory """
        file_path = os.path.join(settings.MEDIA_ROOT, name)
        if Path(file_path).exists():
            return True
        
        return False
    
    def write_xlsx(self, errors):
        """ write errors in xlsx """
        
        workbook = xlwt.Workbook(encoding='utf-8')
        worksheet = workbook.add_sheet(u'Arquivos não encontrados')
        row, col = 0, 0
        
        headers = [
            'Modelo',
            'PK', 
            'Campo',
            'Path',
        ]
        
        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        for col_num in range(len(headers)):
            worksheet.write(row, col_num, headers[col_num], font_style)
        
        font_style = xlwt.XFStyle()
        for error in errors:
            row += 1
            
            _errors =[
                error['model'],
                error['pk'],
                error['field'],
                error['file']
            ]
            
            for col in range(len(_errors)):
                worksheet.write(row, col, _errors[col], font_style)
        
        self.workbook = workbook
        
    def return_xlsx(self):
        """ write errors in xlsx """
        self.workbook.save(self.save_path)
