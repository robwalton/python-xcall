"""Setup script based on the PYPA standard

    https://packaging.python.org/tutorials/packaging-projects/
"""
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="xcall",
    version="1.0.1",
    author="Rob Walton",
    author_email="author@example.com",
    description="Python x-callback-url client for macOS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/robwalton/python-xcall",
    py_modules = ['xcall'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
