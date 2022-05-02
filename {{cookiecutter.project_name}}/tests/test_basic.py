import {{cookiecutter.package_name}}


def test_package_has_version(): # noqa: D103
    {{cookiecutter.package_name}}.__version__


def test_fails():
    assert 1 == 0
