from setuptools import setup, find_packages

setup(
    name="ikats",
    version="1.0",
    url='http://www.c-s.fr',
    license='TBD',
    description="Django app. for algorithms management",
    author='IKATS',
    packages=find_packages(),
    package_dir={'apps': 'ikats/processing/apps', 'ikats': 'ikats', 'contrib': 'ikats/algos/contrib'},
    test_suite="nose.collector",
    tests_require=[
        'mock==2.0.0',
        'py4j==0.10.3',
        'httpretty==0.8.14'
    ],
    install_requires=[
        'setuptools==33.1.1',
        'requests==2.8.1',
        'numpy==1.12.1',
        'scipy==0.18.1',
        'py4j==0.10.3',
        'cffi==1.8.3',
    ],
)
