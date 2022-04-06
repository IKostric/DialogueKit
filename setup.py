import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


packages = setuptools.find_packages(where="dialoguekit")

setuptools.setup(
    name="dialoguekit",
    version="0.0.1",
    author="Jafar Afzali, Krisztian Balog, Aleksander Drzewiecki \
        and Shuo Zhang",
    author_email="author@example.com",
    description="This is a test of packaging",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/iai-group/dialoguekit",
    project_urls={
        "Bug Tracker": "https://github.com/iai-group/dialoguekit/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache 2.0",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "."},
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    zip_safe=False,
    install_requires=["rasa==3.0.8"],
)

# package_dir={"": "src"},