from setuptools import setup, find_packages

setup(
    name = "pypac",
    version = "0.0.9",
    packages=find_packages(),
    install_requires=['pyglet>=1.1.4'],
    extras_require={
    },
    package_data = {},
    author="David Barnett",
    author_email = "davidbarnett2@gmail.com",
    description = "Interactive environment for learning Python programming",
    license = "",
    keywords= "",
    test_suite='nose.collector',
    tests_require=['nose'],
    url = "http://github.com/dbarnett/pypac",
    entry_points = {
        "console_scripts": [
        ]
    }
)
