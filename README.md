# PDF Merger / PDF 合并工具

A small desktop app for merging multiple PDF files into one output file.

一个用于将多个 PDF 文件合并成一个文件的桌面小工具。

## Features / 功能

- Add multiple PDF files.
- Merge files in the order shown in the list.
- Remove files, clear the list, and move files up or down.
- Choose a custom output location.
- Switch the UI between Chinese and English.
- Keep metadata from the first PDF by default.

- 添加多个 PDF 文件。
- 按列表顺序合并文件。
- 支持移除、清空、上移和下移。
- 自定义输出位置。
- 支持中文和英文界面切换。
- 默认保留第一个 PDF 的元数据。

## Quick Start / 快速开始

Double-click `run.bat`.

双击 `run.bat`。

On first launch, the script creates a local `.venv` virtual environment and installs dependencies from `requirements.txt`.

首次运行时，脚本会自动创建本地 `.venv` 虚拟环境，并安装 `requirements.txt` 中的依赖。

## Project Structure / 项目结构

- `pdf_merger_app.py`: Tkinter desktop UI.
- `pdf_tools.py`: PDF operation interfaces and merge implementation.
- `i18n.py`: Chinese and English translations.
- `requirements.txt`: Python dependencies.
- `run.bat`: Windows launch script.

- `pdf_merger_app.py`：Tkinter 桌面界面。
- `pdf_tools.py`：PDF 操作接口和合并实现。
- `i18n.py`：中文和英文翻译。
- `requirements.txt`：Python 依赖。
- `run.bat`：Windows 启动脚本。

## Extension API / 扩展接口

The core PDF logic is separated from the UI so new operations can be added later:

核心 PDF 逻辑与 UI 分离，后续可以继续添加新操作：

- `PdfOperation`: operation protocol.
- `MergePdfOperation`: current merge implementation.
- `PdfOperationRegistry`: registry for future operations such as splitting, compression, and watermarking.

- `PdfOperation`：操作协议。
- `MergePdfOperation`：当前合并实现。
- `PdfOperationRegistry`：用于注册拆分、压缩、加水印等后续操作。

## License / 许可证

Recommended license: MIT.

推荐许可证：MIT。
