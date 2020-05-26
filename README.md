# python-omexml
This is a python interpretation for [OME-2016-06](http://www.openmicroscopy.org/Schemas/Documentation/Generated/OME-2016-06/ome.html)

# Functions
- Fully editing the structure of ome-tiff.xml following [OME-2016-06](http://www.openmicroscopy.org/Schemas/Documentation/Generated/OME-2016-06/ome.html) convention
- Edit and read the values in the ome-tiff.xml. (potentially also for the elementTree or SubElementTree)

# To-do list
- More docstring
- Separate the python-omexml as standalone package for pypi-use

# How to run tests
- Make sure you go to the root directory of the repository.
```
cd path/to/Pyomexml
git checkout develop
python3 -m pip install .
```
- Read the [pytest documentation](https://docs.pytest.org/en/latest/contents.html#) for more info.
