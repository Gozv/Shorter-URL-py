from setuptools import setup, find_packages

setup(
    name="url_shortener",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'flask',
        'validators',
        'python-dotenv'
    ],
    entry_points={
        'console_scripts': [
            'url-shortener=app:main'
        ]
    },
)