from setuptools import setup, find_packages

setup(
    name="ikats",
    version="1.0",
    url='http://your.url.com',
    license='BSD',
    description="Django app. for algorithms management",
    author='IKATS',
    packages=find_packages(),
    package_dir={'apps': 'ikats/processing/apps', 'ikats': 'ikats', 'contrib': 'ikats/algos/contrib'},
    tests_require=[
        'mock', 'py4j'
    ],
    install_requires=['setuptools', 'numpy', 'scipy', 'py4j', 'ikats_core', 'ikats_algo', 'cffi', 'setuptools'],
)
