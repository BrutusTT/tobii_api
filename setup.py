from setuptools import setup, find_packages

version = 0.1

setup( name                 = 'tobii_api',
       version              = version,
       description          = "Tobii API for Python",
       long_description     = open("README.md").read(),
       # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
       classifiers          = [
         "Programming Language :: Python",
         "Topic :: Software Development :: Libraries :: Python Modules",
         ],
       keywords             = '',
       author               = 'Ingo Keller',
       author_email         = 'brutusthetschiepel@gmail.com',
       url                  = '',
       license              = 'LGPL v3',
       packages             = find_packages(exclude=[]),
       namespace_packages   = [],
       include_package_data = True,
       zip_safe             = False,
       install_requires     = [
           'setuptools',
           # -*- Extra requirements: -*-
       ],
       entry_points         = """
       # -*- Entry points: -*-
       """,
     )
