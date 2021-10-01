# django-workflow example project
This example Django project demonstrates how to incorporate 
`django-workflow-engine` into you Django application.


## Getting started
All operations can be completed using the Makefile targets provided. Run
all `make` commands from the repository root. For a complete list of all
make targets, run:

    make

The easiest way to run locally is to use the `docker-compose` configuration 
provided as follows:

```bash
# Build
make build

# Set up
make first-use

# Start in foreground (ctrl+c to stop)
make up
```

Navigate a browser to:

- http://localhost:8000

# Simple case usage
> TODO - Configure two workflows, one trivial and one more elaborate

# Adding your own tasks and views
> TODO - describe building custom tasks and views
 
# Overriding templates
> TODO - describe overriding the build in templates

# Task follow-up
You can configure follow-up notifications on incomplete tasks, ensuring that 
workflow actors get periodic email notifications on incomplete tasks they 
are responsible for.

> TODO - describe workflow config for this

# Applying authorisation to workflow steps

> TODO - describe workflow config for this
