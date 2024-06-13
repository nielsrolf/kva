from setuptools import setup, find_packages

setup(
    name='kva',
    version='0.1.0',
    description='Key-Value-Artifact Logger',
    author='Niels Warncke',
    url='https://github.com/nielsrolf/kva',  # Update with your repo URL
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'pandas',
        'fastapi',
        'fastapi-cors'
    ],
    entry_points={
        'console_scripts': [
            'kva-ui = kva.server:main',  # This assumes server.py has a main() function
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
