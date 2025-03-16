from setuptools import setup, Extension

# Define the C extension
module = Extension(
    "pynamo._conversion",
    sources=["src/pynamo/_conversion.c"],
    extra_compile_args=["-O3"],  # Enable optimization
)

# Setup
setup(
    name="pynamo",
    version="0.1.0",
    packages=["pynamo"],
    package_dir={"": "src"},
    ext_modules=[module],
)
