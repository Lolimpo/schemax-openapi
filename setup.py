from setuptools import find_packages, setup


def find_required():
    with open("requirements.txt") as f:
        return f.read().splitlines()


def find_dev_required():
    with open("requirements-dev.txt") as f:
        return f.read().splitlines()


setup(
    name="schemax-openapi",
    version="0.1.0",
    description="Useful OpenAPI parser for d42 universe",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Nikita Mikheev",
    author_email="thelol1mpo@gmail.com",
    python_requires=">=3.10",
    url="https://github.com/Lolimpo/schemax-openapi",
    packages=find_packages(),
    package_data={"schemax-openapi": ["py.typed"]},
    install_requires=find_required(),
    tests_require=find_dev_required(),
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Typing :: Typed",
    ],
)
