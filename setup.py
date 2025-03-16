from setuptools import setup, Extension

# Define the C extension
module = Extension(
    "pynamo._pynamo",
    sources=[
        "src/pynamo/_pynamo/deserialize_integer.c",
        "src/pynamo/_pynamo/deserialize_decimal.c",
        "src/pynamo/_pynamo/pynamo.c",
    ],
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
