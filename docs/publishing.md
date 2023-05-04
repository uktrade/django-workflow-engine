# Pushing to PyPI

- [PyPI Package](https://pypi.org/project/django-workflow-engine/)
- [Test PyPI Package](https://test.pypi.org/project/django-workflow-engine/)

## Commands

- Running `make build-package` will build the package into the `dist/` directory.
- Running `make push-pypi-test` will push the built package to Test PyPI.
- Running `make push-pypi` will push the built package to PyPI.

## Setting up poetry for pushing to PyPI

First you will need to add the test pypy repository to your poetry config:

```
poetry config repositories.test-pypi https://test.pypi.org/legacy/
```

Then go to https://test.pypi.org/manage/account/token/ and generate a token.

Then add it to your poetry config:

```
poetry config pypi-token.test-pypi XXXXXXXX
```

Then you also need to go to https://pypi.org/manage/account/token/ to generate a token for the real PyPI.

Then add it to your poetry config:

```
poetry config pypi-token.pypi XXXXXXXX
```

Now the make commands should work as expected.
