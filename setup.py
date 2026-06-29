from setuptools import setup, find_packages

setup(
    name="py-android",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "click>=8.0.0",
        "jinja2>=3.0.0",
        "gdown>=5.0.0",
        "tqdm>=4.66.0",
    ],
    entry_points={
        "console_scripts": [
            "py-android=py_android.cli:main",
        ],
    },
)