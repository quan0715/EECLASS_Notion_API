from setuptools import find_packages, setup

setup(
    name='eeclass_bot',
    version='0.0.41',
    author='Quan',
    author_email='quan787887@gmail.com',
    packages=find_packages(
        include=['eeclass_bot'],
    ),
    package_data={
        'eeclass_bot': ['models/*'],  # 包含 data_folder 文件夹中的所有内容
    },
    url='https://github.com/quan0715/EECLASS_Notion_API/',
    license='license.txt',
    description='EECLASS 爬蟲API機器人',
    # long_description=open('ReadMe.md').read(),
    install_requires=[
        "requests >= 2.18.4",
        "beautifulsoup4 >= 4.9.3",
        "fake-user-agent >= 2.1.8",
        "aiohttp >= 3.8.3",
        "selenium >= 4.14.0",
        "PySocks >= 1.7.1"
    ],
)
