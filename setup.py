from setuptools import find_packages, setup

setup(
    name='eeclass_bot',
    version='0.0.2',
    author='Quan',
    author_email='quan787887@gmail.com',
    packages=find_packages(
        include=['eeclass_bot', 'eeclass_bot.*'],
    ),
    url='https://github.com/quan0715/EECLASS_Notion_API/',
    license='license.txt',
    description='EECLASS 爬蟲API機器人',
    # long_description=open('ReadMe.md').read(),
    install_requires=[
        "requests >= 2.18.4",
        "beautifulsoup4 >= 4.9.3",
        "fake-user-agent >= 2.1.8",
        "aiohttp >= 3.8.3",
    ],
)
