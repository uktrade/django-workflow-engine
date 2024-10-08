from setuptools import find_packages, setup

with open("docs/index.md", "r") as fh:
    long_description = fh.read()

setup(
    name="django-workflow-engine",
    version="0.2.2",
    packages=find_packages(),
    include_package_data=True,
    author="DIT Live Service Team",
    author_email="live.services@digital.trade.gov.uk",
    url="https://github.com/uktrade/django-workflow-engine",
    description="Lightweight, reusable workflow engine for Django applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "django>=3.2.15",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
