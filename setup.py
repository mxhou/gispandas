from setuptools import setup, find_packages
from os import path
this_directory = path.abspath(path.dirname(__file__))
filepath = path.join(this_directory, 'README.md')
VERSION = '0.1.9'
setup(
    name='gispandas',  # package name
    version=VERSION,  # package version
    author="HMX",
    author_email="kzdhb8023@163.com",
    description='gispandas',  # package description
    packages=find_packages(),
    url="https://github.com/mxhou/gispandas/",
    zip_safe=False,
    # What packages are required for this module to be executed?
    REQUIRED = ['geopandas', 'numpy','json','rasterio','rasterstats','gdal'],
    license='MIT',
    python_requires=">=3.6",
    keywords=['gis','geo','tif','json','shp'],
    data_files=[filepath],
    long_description=open(filepath, encoding='utf-8').read(),
    long_description_content_type='text/markdown'
)