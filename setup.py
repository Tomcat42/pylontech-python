from setuptools import setup, find_packages


setup(
    name="pylontech",
    version="0.1.1",
    packages=find_packages(include=['pylontech', 'pylontech.*']),
    url="https://github.com/Tomcat42/pylontech-python/",
    author="Bernd Singer",
    author_email="singer@nefkom.net",
    description=("Communicate to Pylontech batteries using a RS485 interface"),
    license="MIT",
    keywords="pylontech pylon RS485 lithium battery US2000 US2000C US3000",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=["pyserial"],
)
