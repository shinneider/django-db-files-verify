# -*- coding: utf-8 -*-
#!/usr/bin/env python

from io import open

from setuptools import find_packages, setup

from django_db_files_verify.meta import VERSION

setup(
    name='django-db-files-verify',
    version=str(VERSION),
    description='This project verify your db files exists in storage and save errors in xlsx',
    long_description=open('README.md', encoding='utf-8').read(),
    author='Shinneider Libanio da Silva',
    author_email='shinneider-libanio@hotmail.com',
    url='https://github.com/shinneider/django_admin_related',
    license='MIT',
    packages=find_packages() + [
        'django_admin_related/templates', 
        'django_admin_related/locale'
    ],
    install_requires=[
        'xlwt>=1.3.0',
    ],
    include_package_data=True,
)