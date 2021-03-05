# Pyramid API Starter
![](https://github.com/RobinSiep/cookiecutter-pyramid-api/workflows/Test/badge.svg)
[![codecov](https://codecov.io/gh/RobinSiep/cookiecutter-pyramid-api/branch/master/graph/badge.svg?token=PP7DQ89YCI)](https://codecov.io/gh/RobinSiep/cookiecutter-pyramid-api)

This [Cookiecutter](https://cookiecutter.readthedocs.io/en/1.7.2/README.html) template generates an opinionated API project using [Pyramid](https://trypyramid.com/) that's ready for development.

## Features
The generated project contains the following implementations so that you can focus on impactful features:

* URL traversal using factories.
* [OpenAPI](https://swagger.io/specification/) documentation and decorators to further expand this.
* Cookie-based authentication using email address and password.
* Support for account recovery using [Sendgrid](https://sendgrid.com/).
* Authorization management on all handlers.
* [Dockerfile](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) files for easy development.
* Full unit test coverage.
* Code written according to default [Flake8](https://flake8.pycqa.org/en/latest/#).

## Quickstart
Install the latest Cookiecutter if you haven't yet, for example:
```
pip install -U cookiecutter
```

Generate the project:
```
cookiecutter https://github.com/RobinSiep/cookiecutter-pyramid-api.git
```
