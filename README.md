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

This will read and convert the content in `file.md` into `file.tex`
at the current working directory. After the conversion, use `xelatex file`
to produce a `.pdf` file from the LaTeX source code.

The output filename depends on your input, for `foo.md`, m2l will produce `foo.tex`

这会读取并转换 `file.md` 的内容到当前工作路径的 `file.tex` 文件。在此之后，可以使用
`xelatex file` 来编译产生 pdf

输出的文件名由命令输入决定，对 `foo.md` 的转换会产生 `foo.tex`

## Current progress and plans | 进度，安排

- Currently `m2l` basically supports:
  - plain text, 
  - title, 
  - unordered/ordered lists,
  - pictures (please use a local path if you do so, otherwise you are being impolite to LaTeX.)
  - inline patterns
    - something **bold**
    - something _italic_
    - or something **_bold and italic_**
    - inline `code snippets`
    - [hyperlinks](https://http.cat/404)
- The future versions will focus on equations, codeblocks
- Versions in the more distant future will support DIY markdown grammar and texify methods.

- 现阶段支持了：
  - 文本
  - 标题
  - 有序无序列表
  - 图片（本地路径）
  - 行内样式
    - **粗体**文本
    - *斜体*文本
    - **_又粗又斜_** 的文本（你为什么要这样干）
    - `代码`片段
    - [超链接](https://http.cat/404)
- 未来版本计划支持公式、代码块
- 在更久远的未来，可以支持用户自定义md语法和 texify 方法