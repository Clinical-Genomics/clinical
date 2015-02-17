# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
 
setup(
  name='clinical',
  version='0.0.1',
  long_description=__doc__,
  author='Rikard Erlandsson',
  author_email='rikard.erlandson@scilifelab.se',
  license='MIT',
  url='http://github.com/Clinical-Genomics/clinical',
  packages=find_packages(),
  include_package_data=True,
  zip_safe=False,
)
