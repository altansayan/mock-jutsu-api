from setuptools import setup, find_packages

setup(
    name="mock-jutsu",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "fastapi",
        "uvicorn",
        "click"
    ],
    entry_points={
        "console_scripts": [
            "mockjutsu=mockjutsu.cli:main",
        ],
    },
)
