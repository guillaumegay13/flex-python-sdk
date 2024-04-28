from setuptools import setup, find_packages

setup(
    name='flex',
    version='0.2',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    install_requires=[
        'requests'
    ]
)