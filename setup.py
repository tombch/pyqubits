from setuptools import setup


requirements = ["numpy", "pyreadline"]
setuptools.setup(
    name="cmdquantum",
    author="Thomas Brier",
    version="1.0.0",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    entry_points = {
        'console_scripts': 'cmdquantum = scripts.main:program'
    }
)