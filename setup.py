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
    test_suite="nose.collector",
    tests_require=[
        'mock>=1.3.0', 
        'py4j', 
        'httpretty>=0.8.10'
    ],
    install_requires=[
        'setuptools', 
        'requests>=2.8.1', 
        'numpy', 
        'scipy', 
        'py4j', 
        'cffi', 
    ],
)
