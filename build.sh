# to generate the requirements.txt files use pip-compile from pip-tools
pip-compile requirements/requirements.in 
pip-compile requirements/dev-requirements.in

rm dist/*

# compile the dist
python setup.py bdist_wheel --universal
python setup.py sdist

# upload to pypi
twine upload dist/*
