import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

# read version number from package
import bmondata
ver = bmondata.__version__

setuptools.setup(
    name="bmondata",
    version=ver,
    author="Alan Mitchell",
    author_email="tabb99@gmail.com",
    description="Allows retrieval and storage of data on BMON Servers.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alanmitchell/bmondata",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'requests>=2.18.4',
        'pandas>=0.23.2'
    ]
)