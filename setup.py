from setuptools import setup, find_packages

setup(name='hummingbird',
    version='0.0.1',
    author='Richard Cao',
    author_email='richardycao@gmail.com',
    license='MIT',
    url='https://github.com/richardycao/hummingbird_python.git',
    packages=find_packages(),
    install_requires=['confluent-kafka']
)