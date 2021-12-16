import pathlib
from setuptools import _install_setup_requires, setup, find_packages

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()
setup(
	name = "jsonbyket",
	version = "1.0.0",
	description = "Configure JSON with exisiting json module",
	long_description = README,
	long_description_content_type = "text/markdown",
	url = "https://github.com/mypylibrary/jsonbyket",
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
    ],
	install_requires=[''],
	author = "Ketan Badhe",
	author_email = "badhe.ketan@gmail.com",
	packages=find_packages(),
	include_package_data=True
)

#notes for building and releasing
#python3 -m build
#python3 -m twine upload --repository pypi dist/*