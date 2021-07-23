from setuptools import setup, find_packages

setup(
    name='gmg',
    version='0.1',
    packages=find_packages(),
    py_modules=['cli'],
    install_requires=[
        'Click'
    ],
    entry_points='''
        [console_scripts]
        get_my_groceries=cli:scrape
    '''
)
