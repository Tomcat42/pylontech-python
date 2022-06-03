from setuptools import setup, find_packages


setup(
    name="pylontech",
    version="0.1.0",
    packages=find_packages(include=['pylon', 'pylon.*']),
    author="Bernd Singer",
    author_email="singer@nefkom.net",
    description=("Communicate to Pylontech batteries using a RS485 interface"),
    license="MIT",
    keywords="pylontech pylon rs485 lithium battery US2000 US2000C US3000",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
)
