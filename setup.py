from setuptools import setup, find_packages

setup(
    name="pixelpasta",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.26.0",
        "matplotlib>=3.8.0",
        "scikit-learn>=1.3.0",
        "flask>=2.3.3",
        "werkzeug>=2.3.7",
        "scipy>=1.11.0",
        "pillow>=10.0.0",
        "reportlab>=4.0.4",
    ],
)
