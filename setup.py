from setuptools import setup, find_packages

setup(
    name='getoutline-cli',
    version='0.4.0',
    packages=find_packages(),
    install_requires=[
        'pyyaml',
        'requests',
    ],
    extras_require={
        'dev': [
            'twine',
            'wheel',
            'flake8',
        ],
    },
    entry_points={
        'console_scripts': [
            'getoutline-cli=getoutline_cli.getoutline_cli:main',
        ],
    },
    author='Alexander Pivovarov',
    author_email='pivovarov@gmail.com',
    description='CLI utility for publishing markdown files to Outline wiki',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/bladerunner2020/getoutline-cli.git',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
