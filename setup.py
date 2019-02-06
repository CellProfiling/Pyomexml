import setuptools

setuptools.setup(
    name='pyomexml',
    author='Hao Xu',
    version='0.0.0',
    author_email='hao.xu@scilifelab.se',
    description='A python API for OME-2016-06',
    url='https://github.com/haoxusci/pyomexml',
    license='GNU',
    install_requires=[
        'uuid',
        'datetime',
    ],
    packages=setuptools.find_packages(),
    zip_safe=False)
