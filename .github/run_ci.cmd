cls && flake8 && mypy . --config-file tox.ini --install-types --non-interactive && py -3 -m pytest -vv
