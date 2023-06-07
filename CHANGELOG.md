# CHANGELOG

## 0.2.0

- Update logic to break on a failing task, but also execute any other tasks that aren't failing.

## 0.1.1

- Update requests to 2.31.0
- Update pymdown-extensions to 10.0.1

## 0.1.0

- Add cleanup command to remove duplicate TaskRecords.
- TaskRecord model has been removed.

### Data migrations

This release removes models that you might have referenced in data migrations, you will need to update any of these migrations with the following `run_before` to ensure that your migrations can run successfully:

```python
class Migration(migrations.Migration):
    ...
    run_before = [
        ("django_workflow_engine", "0008_remove_taskrecord_broke_flow"),
    ]
    ...
    operations = [
        ...
    ]
```
