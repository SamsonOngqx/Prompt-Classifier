from setuptools import setup, find_packages
from setuptools.command.install import install
import os
import subprocess

setup(
    name='prompt_classifier',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'joblib',
        'scikit-learn==1.5.2',
        'imblearn',
        'xgboost',
    ],
    description='A Python package for chatbot developers to classify prompt injection attempts.',
    author='Samson Ong',
    author_email='---------------',
)
