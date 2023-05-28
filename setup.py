from setuptools import setup

setup(
    name="GetMyGroceries",
    version="0.0.1",
    packages=[
        "gmg",
        "gmg.utils",
        "gmg.scrapers",
    ],
    include_package_data=True,
    install_requires=["Click"],
    entry_points="""
        [console_scripts]
        gmg=gmg.cli:scrape
    """,
)
