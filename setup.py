import setuptools


setuptools.setup(
    name="pyqubits",
    author="Thomas Brier",
    version="0.2.0",
    packages=setuptools.find_packages(),
    install_requires=[
        "numpy",
        "numba",
    ],
)
