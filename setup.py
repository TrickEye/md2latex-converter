import setuptools

"""
build command:
    `python setup.py sdist bdist_wheel`
upload command (using twine):
    `twine upload dist/*`
"""

from md2latex_converter.version import VERSION

with open('LICENSE.txt', 'r', encoding='utf-8') as f:
    LICENSE = f.read()

with open('README.md', 'r', encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

setuptools.setup(
    name="md2latex_converter",
    version=VERSION,
    author="TrickEye",
    author_email="TrickEye@buaa.edu.cn",
    description="A md-to-LaTeX converter",
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': ['m2l = md2latex_converter.__main__:main', ]
    },
    python_requires='>=3.10',
    install_requires="pyperclip",
    license=LICENSE,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown'
)
