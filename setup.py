from distutils.core import setup

import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="django_workflow",
    version="0.0.1",
    packages=setuptools.find_packages(),
    author="David Charles",
    author_email="david.charles@digital.trade.gov.uk",
    url="https://github.com/uktrade/django-workflow",
    description="Lightweight, reusable workflow engine for Django applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "django>=2.2.24",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)
