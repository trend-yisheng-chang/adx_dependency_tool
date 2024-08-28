from setuptools import setup, find_packages

setup(
    name='adx_dependency_tool',
    version='0.1.0',
    author='Eason YS Chang',
    author_email='eason_ys_chang@trendmicro.com',
    description='A tool for checking dependencies of Azure Data Explorer dashboards.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/trend-yisheng-chang/adx_dependency_tool.git',
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
