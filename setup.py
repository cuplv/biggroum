from setuptools import setup, find_packages

long_description=\
"""
fixrgraph extractor
"""

setup(
    name='fixrgraph',
    version='0.0.1dev1',
    author='PySMT Team',
    author_email='',
    packages = find_packages(),
    include_package_data = True,
    url='https://github.com/cuplv/FixrGraph',
    license='',
    description='',
    long_description=long_description,
    install_requires=["sqlalchemy"],
    entry_points={
        'console_scripts': [
            'fixrgraph-scheduler = fixrgraph.scheduler.create_jobs:main',
            'fixrgraph-process-graphs = fixrgraph.scheduler.process_graphs:main',
            'fixrgraph-process-logs = fixrgraph.scheduler.process_logs:main',
            'fixrgraph-iso-html = fixrgraph.provenance:gen_html:main',
        ],
    },
)

