from setuptools import setup, find_packages
from setuptools.command.install import install

setup(
    name='prompt_classifier',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'joblib==1.4.2',
        'scikit-learn==1.5.2',
        'imblearn',
        'xgboost==2.1.3',
    ],
    description='A Python package for chatbot developers to classify prompt injection attempts.',
    author='Samson Ong',
    author_email='---------------',
)
