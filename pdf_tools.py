from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Protocol

from pypdf import PdfReader, PdfWriter


@dataclass(frozen=True)
class MergeOptions:
    output_path: Path
    keep_metadata: bool = True


@dataclass(frozen=True)
class CompressOptions:
    output_path: Path
    target_size_mb: float = 10.0
    remove_metadata: bool = True


@dataclass(frozen=True)
class PdfOperationResult:
    output_path: Path
    output_size_bytes: int
    target_size_bytes: int | None = None

    @property
    def is_over_target(self) -> bool:
        return self.target_size_bytes is not None and self.output_size_bytes > self.target_size_bytes


class PdfMergeError(Exception):
    def __init__(self, code: str, **details: object):
        super().__init__(code)
        self.code = code
        self.details = details


class PdfOperation(Protocol):
    name: str

    def run(self) -> PdfOperationResult:
        ...


class MergePdfOperation:
    name = "merge"

    def __init__(self, pdf_paths: Iterable[Path], options: MergeOptions):
        self.pdf_paths = [Path(path) for path in pdf_paths]
        self.options = options

    def run(self) -> PdfOperationResult:
        if len(self.pdf_paths) < 2:
            raise PdfMergeError("error_min_files")

        writer = PdfWriter()
        first_metadata_added = False

        for pdf_path in self.pdf_paths:
            if not pdf_path.exists():
                raise PdfMergeError("error_missing_file", path=pdf_path)

            reader = PdfReader(str(pdf_path))
            if reader.is_encrypted:
                raise PdfMergeError("error_encrypted_pdf", name=pdf_path.name)

            if self.options.keep_metadata and not first_metadata_added and reader.metadata:
                writer.add_metadata(dict(reader.metadata))
                first_metadata_added = True

            for page in reader.pages:
                writer.add_page(page)

        self.options.output_path.parent.mkdir(parents=True, exist_ok=True)
        with self.options.output_path.open("wb") as output_file:
            writer.write(output_file)

        return PdfOperationResult(
            output_path=self.options.output_path,
            output_size_bytes=self.options.output_path.stat().st_size,
        )


class CompressPdfOperation:
    name = "compress"

    def __init__(self, pdf_path: Path, options: CompressOptions):
        self.pdf_path = Path(pdf_path)
        self.options = options

    def run(self) -> PdfOperationResult:
        if not self.pdf_path.exists():
            raise PdfMergeError("error_missing_file", path=self.pdf_path)

        if self.options.target_size_mb <= 0:
            raise PdfMergeError("error_invalid_target_size")

        reader = PdfReader(str(self.pdf_path))
        if reader.is_encrypted:
            raise PdfMergeError("error_encrypted_pdf", name=self.pdf_path.name)

        writer = PdfWriter()
        for page in reader.pages:
            page.compress_content_streams()
            writer.add_page(page)

        if not self.options.remove_metadata and reader.metadata:
            writer.add_metadata(dict(reader.metadata))

        self.options.output_path.parent.mkdir(parents=True, exist_ok=True)
        with self.options.output_path.open("wb") as output_file:
            writer.write(output_file)

        target_size_bytes = int(self.options.target_size_mb * 1024 * 1024)
        return PdfOperationResult(
            output_path=self.options.output_path,
            output_size_bytes=self.options.output_path.stat().st_size,
            target_size_bytes=target_size_bytes,
        )


class PdfOperationRegistry:
    def __init__(self) -> None:
        self._operations: dict[str, type[PdfOperation]] = {}

    def register(self, operation_cls: type[PdfOperation]) -> None:
        self._operations[operation_cls.name] = operation_cls

    def names(self) -> list[str]:
        return sorted(self._operations)


operation_registry = PdfOperationRegistry()
operation_registry.register(MergePdfOperation)
operation_registry.register(CompressPdfOperation)
