from setuptools import setup, find_packages

setup(
    name="st_approx",
    version="0.1",
    packages=find_packages(),
    install_requires=['numpy', 'matplotlib', 'scipy'], # Зависимости установятся сами
)