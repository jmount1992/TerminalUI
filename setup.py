import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="terminalui",
    version="0.1.3",
    author="James Mount",
    author_email="jmount1992@gmail.com",
    description="A Python Terminal User Interface based on urwid with asynchronous input/output that can be easily expanded to your application.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jmount1992/TerminalUI",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'urwid>=2.1.2',
    ]

)