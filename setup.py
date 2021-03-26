from setuptools import setup

setup(name='hummingbird',
    version='0.0.1',
    author='Richard Cao',
    author_email='richardycao@gmail.com',
    license='MIT',
    url='https://github.com/richardycao/hummingbird_python.git',
    packages=['hummingbird'],
    install_requires=['confluent-kafka==1.6.0']
)