# `md2latex-converter` introduction 

> `pip install md2latex-converter`

`md2latex-converter` is a Python package that helps
to convert a .md (Markdown) file into a .tex (LaTeX)
file, with special support for Chinese, using the `ctex`
package provided by the LaTeX community.

`md2latex-converter` 是一个将 Markdown 文件转换成 LaTeX 
源代码的 Python 工具包。使用了 LaTeX 的 `ctex` 包，因此对于
中文的编码环境有特别的关照。

## Installation and Usage | 安装与使用

`pip install md2latex-converter`

This will install the package into your current python 
interpreter. The installation will add `m2l.exe` into 
the `Scripts` folder of python (on Windows) or `m2l` 
into `~/.local/bin/` by default (on Linux), if you have 
previously added the path above into your system PATH 
variable, you should be able to invoke the program 
through the command `m2l`.

这会在现有的 Python 解释器中安装此包。安装过程中会将 `m2l.exe` 安装在
当前的 Python 的 `Scripts` 路径（Windows）或默认将 `m2l` 安装到 
`~/.local/bin/` 路径（Linux）。如果此前已经将这个路径加入了 PATH 变量，
那么可以通过 `m2l` 指令来运行此程序。

`m2l file.md`

This will read and convert the content in `file.md` into `output.tex`
at the current working directory. After the conversion, use `xelatex output`
to produce a `.pdf` file from the LaTeX source code.

这会读取并转换 `file.md` 的内容到当前工作路径的 `output.tex` 文件。在此之后，可以使用
`xelatex output` 来编译产生 pdf