from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='bobcat',
      version=version,
      description="",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Wes Turner',
      author_email='wes.turner@gmail.com',
      url='',
      license='New BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          #'FuXi'==1.1,
            # pip install -e hg+https://fuxi.googlecode.com/hg/#egg=FuXi
            #'http://pypi.python.org/packages/source/F/FuXi/FuXi-1.1.production.tar.gz#md5=34ed6ff38785ae2609ba7dbff8051366',
      ],
      entry_points={
          'console_scripts':[
                'bobcat = bobcat:main',
              ],
          },
      )
