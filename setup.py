from importlib.metadata import entry_points
from setuptools import setup, find_packages

setup(
    name='xlsform',
    version='0.0.1',
    description='XLSForm Helper Tools',
    author='Marcel Gietzmann-Sanders',
    author_email='marcelsanders96@gmail.com',
    packages=find_packages(include=['xlsform', 'xlsform*']),
    install_requires=[
        'openpyxl',
        'click',
        'pytest'
    ],
    entry_points={
        'console_scripts': [
            'xlsform=xlsform.__init__:xlsform'
        ]
    }
)