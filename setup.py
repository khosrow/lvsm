# from distutils.core import setup
from setuptools import setup, find_packages
import lvsm

setup(
    name='lvsm',
    version=lvsm.__version__,
    author=lvsm.__author__,
    author_email='khosrow@khosrow.ca',
    packages=find_packages(exclude='tests'),
    url='https://github.com/khosrow/lvsm',
    license='LICENSE.rst',
    description=lvsm.__doc__.strip(),
    long_description="\n\n".join([open('README.rst').read(),
                                  open('CHANGES.rst').read()]),
    entry_points={
        'console_scripts': [
            'lvsm = lvsm.__main__:main',
            'kaparser = lvsm.modules.kaparser:main',
        ],
    },
    test_suite="tests",
    data_files=[('share/doc/lvsm/samples', ['samples/lvsm.conf.sample'])] 
)
