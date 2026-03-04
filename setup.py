from Cython.Build import cythonize
from setuptools import Extension, setup

setup(
    ext_modules=cythonize(
        [Extension("*", sources=["pydub/*.pyx"], extra_compile_args=["-march=native", "-O3"])],
        compiler_directives={"language_level": "3"},
    ),
)
