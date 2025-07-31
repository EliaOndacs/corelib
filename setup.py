from setuptools import setup, find_packages

setup(
    name="corelib",
    version="1.7.0",
    author="EliaOndacs",
    author_email="amirreza.ondacs90@gmail.com",
    description="an all in one package for building nice python application",
    long_description=open("Readme.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/EliaOndacs/corelib",
    packages=find_packages(),
    license="license",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.13",
)
