from setuptools import setup

import ratelimit


def readme():
    '''Read README file'''
    with open('README.rst') as infile:
        return infile.read()

setup(
    name='ratelimit',
    version=ratelimit.__version__,
    description='API rate limit decorator',
    long_description=readme().strip(),
    author='',
    author_email='',
    url='https://github.com/trycoast/ratelimit',
    license='MIT',
    packages=['ratelimit'],
    install_requires=[],
    keywords=[
        'ratelimit',
        'api',
        'decorator'
    ],
    include_package_data=True,
    zip_safe=False
)
