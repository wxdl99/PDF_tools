# PDF Tools / PDF 工具

A small desktop app for merging PDF files and reducing PDF file size.

一个用于合并 PDF 文件、减小 PDF 文件体积的桌面小工具。

## Features / 功能

- Add multiple PDF files.
- Merge files in the order shown in the list.
- Compress a single PDF and check whether it is under the target size, such as 10 MB.
- Remove files, clear the list, and move files up or down.
- Choose a custom output location.
- Switch the UI between Chinese and English.
- Keep or remove PDF metadata.

- 添加多个 PDF 文件。
- 按列表顺序合并文件。
- 压缩单个 PDF，并检查是否小于目标大小，例如 10 MB。
- 支持移除、清空、上移和下移。
- 自定义输出位置。
- 支持中文和英文界面切换。
- 支持保留或移除 PDF 元数据。

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
- `CompressPdfOperation`: current compression implementation.
- `PdfOperationRegistry`: registry for future operations such as splitting, image downsampling, and watermarking.

- `PdfOperation`：操作协议。
- `MergePdfOperation`：当前合并实现。
- `CompressPdfOperation`：当前压缩实现。
- `PdfOperationRegistry`：用于注册拆分、图片降采样、加水印等后续操作。

## Compression Notes / 压缩说明

The current compression mode rewrites the PDF, compresses page content streams, and can remove metadata. This is safe for normal PDFs, but it cannot always force image-heavy scanned PDFs below a target such as 10 MB. The app will show the final file size and warn you if the output is still larger than the target.

当前压缩模式会重写 PDF、压缩页面内容流，并可移除元数据。这个方式对普通 PDF 比较稳妥，但如果文件主要由大图片或扫描页组成，不一定能强制压到 10 MB 以下。软件会显示最终文件大小，如果仍超过目标大小会给出提醒。

## License / 许可证

Recommended license: MIT.

推荐许可证：MIT。
