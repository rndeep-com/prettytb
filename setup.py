import setuptools



setuptools.setup(
    name = "prettytb",
    description="Prints stack tracebacks showing each frame's local variables and improves visual feedback using colors.",
    packages = setuptools.find_packages(exclude=['tests*']),
    version="1.0.0",
    install_requires = [
        "future",
    ]
)
