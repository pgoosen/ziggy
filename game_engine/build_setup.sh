pipenv lock
pipenv lock -r > requirements.txt
pipenv run python -m pip install --upgrade setuptools wheel
pipenv run python setup.py sdist bdist_wheel
