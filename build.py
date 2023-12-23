import shutil
from pathlib import Path

from Cython.Build import cythonize
from setuptools import Distribution, Extension
from setuptools.command.build_ext import build_ext


def build() -> None:
    extensions = [
        Extension(
            "*",
            sources=["pydub/*.pyx"],
            libraries=["m"],  # math library
            include_dirs=[],
            extra_compile_args=["-march=native", "-O3"],
        )
    ]

    ext_modules = cythonize(
        module_list=extensions,
        compiler_directives={
            "language_level": "3",
        },
    )

    distribution = Distribution({"ext_modules": ext_modules})
    cmd = build_ext(distribution)
    cmd.finalize_options()
    cmd.run()

    for output in cmd.get_outputs():
        relative_extension = Path(output).relative_to(cmd.build_lib)
        shutil.copyfile(output, relative_extension)


if __name__ == "__main__":
    build()
