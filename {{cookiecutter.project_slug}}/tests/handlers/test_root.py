from {{cookiecutter.project_slug}} import VERSION


def test_root(test_app):
    response = test_app.get('/')
    assert response.json == {'version': VERSION}
