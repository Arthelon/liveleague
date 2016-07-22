from setuptools import setup

setup(
    name="liveleague",
    author="Daniel Hsing",
    author_email="hsing.daniel@gmail.com",
    license="MIT",
    version="0.1",
    description="Command-line utility that reveals valuable insight about allies and team-mates during a live League "
                "of Legends match.",
    scripts=["bin/liveleague"],
    packages=["liveleague"]
)