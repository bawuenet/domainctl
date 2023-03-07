from setuptools import setup
from setuptools import find_packages

version = "0.1.0"

install_requires = ["setuptools", "requests", "bs4", "dnspython", "tabulate", "PyYAML"]

# read the contents of your README file
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md")) as f:
    long_description = f.read()

setup(
    name="bawuenet-domainctl",
    version=version,
    description="bawue.net DNS API client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bawuenet/domainctl",
    author="Andreas",
    author_email="andreas@bawue.net",
    license="GPL v3",
    python_requires=">=3.5",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: System :: Networking",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
#    packages=["bawuenet"],
    scripts=["domainctl.py"],
    #    test_suite="certbot_dns_bawuenet",
)
