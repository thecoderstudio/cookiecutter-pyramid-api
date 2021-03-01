from http import HTTPStatus


def test_get_spec(test_app):
    response = test_app.get('/openapi')

    assert response.status_code == HTTPStatus.OK
    assert response.json
