from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='sdmdl',    
    version='0.1.0',    
    description='Species Distribution Modelling using Deep Learning',    
    long_description=readme,    
    author='Winand Hulleman, Wouter Koch, Rutger Vos',    
    author_email='winand@live.nl, wouter.koch@artsdatabanken.no, rutger.vos@naturalis.nl',    
    url='https://github.com/naturalis/trait-geo-diverse-angiosperms',    
    license=license,    
    packages=find_packages(exclude=('tests', 'docs', 'data', 'script')),                           
)
