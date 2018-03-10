from setuptools import setup, find_packages

setup(
	name="Candytuft",
	version="0.1",
	author="Anton Kolmakov",
	author_email="anton@kolmakov.me",
	packages=find_packages(),
	install_requires=[
		"selenium==3.10.0",
		"ujson==1.35"
	]
)
