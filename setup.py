from setuptools import setup, find_packages

setup(
	name="candytuft",
	version="0.1",
	author="Anton Kolmakov",
	author_email="anton@kolmakov.me",
	packages=find_packages(),
	python_requires=">=3",
	entry_points={
		"console_scripts": [
			"candytuft=candytuft.launcher:candytuft"
		]
	},
	install_requires=[
		"selenium==3.10.0",
		"ujson==1.35",
		"flask==0.12.2",
		"boto3==1.6.6"
	]
)
