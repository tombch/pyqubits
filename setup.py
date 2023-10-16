import setuptools


setuptools.setup(
    name="pyqubits",
    author="Thomas Brier",
    version="0.2.1",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=[
        "numpy",
        "numba",
    ],
)
