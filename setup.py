from setuptools import setup, find_packages

setup(
    name="bpcs-steg",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "Pillow",
        "numpy",
    ],
    entry_points={
        "console_scripts": [
            "bpcs-steg=cli:main",
        ],
    },
)