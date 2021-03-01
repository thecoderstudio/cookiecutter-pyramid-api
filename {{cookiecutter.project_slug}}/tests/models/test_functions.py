from {{cookiecutter.project_slug}}.models.functions import pg_utcnow


def test_pg_utcnow():
    assert pg_utcnow(None, None) == "TIMEZONE('utc', CURRENT_TIMESTAMP)"
