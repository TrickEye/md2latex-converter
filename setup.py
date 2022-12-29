import setuptools

VERSION = "0.0.1"

setuptools.setup(
    name="md2latex_converter",
    version=VERSION,
    author="TrickEye",
    author_email="TrickEye@buaa.edu.cn",
    description="A md-to-LaTeX converter",
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': ['m2l = md2latex_converter.__main__:main', ]
    }
)
