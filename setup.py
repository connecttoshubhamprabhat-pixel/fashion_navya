from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in fashion_navya/__init__.py
from fashion_navya import __version__ as version

setup(
	name="fashion_navya",
	version=version,
	description="navya fashion",
	author="pawasthy11@gmail.com",
	author_email="pawasthy11@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
