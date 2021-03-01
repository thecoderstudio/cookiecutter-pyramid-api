from {{cookiecutter.project_slug}}.lib.resources import LocationAwareResource


def test_location_aware_resource_name():
    class Sample(LocationAwareResource):
        pass

    sample = Sample()

    assert sample.__name__ == 'Sample'
