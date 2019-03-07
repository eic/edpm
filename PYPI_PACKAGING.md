TL;DR;   

```bash
python3 -m pip install --user --upgrade setuptools wheel
python3 setup.py sdist bdist_wheel

python3 -m pip install -r requirements.txt --user
python3 -m twine upload dist/*
```

A tutorial:
https://packaging.python.org/tutorials/packaging-projects/

ejpm pip: https://pypi.org/project/ejpm/#history




