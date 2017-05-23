from setuptools import setup, find_packages
import os
import re
import ast


def get_requirements(suffix=''):
    BASE_PATH = os.path.join(os.path.dirname(__file__), 'requirements')
    with open(os.path.join(BASE_PATH, 'requirements%s.txt' % suffix)) as f:
        rv = f.read().splitlines()
        return rv

def get_version(file):
    _version_re = re.compile(r'__version__\s+=\s+(.*)')

    with open(file, 'rb') as f:
        version = str(ast.literal_eval(_version_re.search(
            f.read().decode('utf-8')).group(1)))
        return version


setup(
    name='Flask-Prose',
    version=get_version('flask_prose/__init__.py'),
    url='https://github.com/slippers/Flask-Prose',
    license='MIT',
    author='Kirk Erickson',
    author_email='ekirk0@gmail.com',
    description='A flask extension for generating markov prose',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=get_requirements(),
    tests_require=['pytest'],
    test_suite='tests',
    classifiers=[
        'Development Status :: 1 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
