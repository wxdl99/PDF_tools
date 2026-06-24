from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import tempfile
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
            writer.add_page(page)
            writer.pages[-1].compress_content_streams()

        if not self.options.remove_metadata and reader.metadata:
            writer.add_metadata(dict(reader.metadata))

        self.options.output_path.parent.mkdir(parents=True, exist_ok=True)
        with self.options.output_path.open("wb") as output_file:
            writer.write(output_file)

        target_size_bytes = int(self.options.target_size_mb * 1024 * 1024)
        if self.options.output_path.stat().st_size > target_size_bytes:
            self._write_downsampled_pdf(target_size_bytes)

        return PdfOperationResult(
            output_path=self.options.output_path,
            output_size_bytes=self.options.output_path.stat().st_size,
            target_size_bytes=target_size_bytes,
        )

    def _write_downsampled_pdf(self, target_size_bytes: int) -> None:
        try:
            import fitz
        except ImportError as exc:
            raise PdfMergeError("error_missing_compression_dependency") from exc

        profiles = [
            (150, 76),
            (130, 72),
            (110, 68),
            (96, 64),
            (82, 58),
            (72, 52),
        ]
        best_path: Path | None = None
        best_size: int | None = None

        with tempfile.TemporaryDirectory() as temp_dir_name:
            temp_dir = Path(temp_dir_name)
            for dpi, jpeg_quality in profiles:
                candidate = temp_dir / f"compressed_{dpi}_{jpeg_quality}.pdf"
                self._render_image_pdf(candidate, dpi=dpi, jpeg_quality=jpeg_quality, fitz=fitz)
                candidate_size = candidate.stat().st_size

                if best_size is None or candidate_size < best_size:
                    best_path = candidate
                    best_size = candidate_size

                if candidate_size <= target_size_bytes:
                    best_path = candidate
                    break

            if best_path is None:
                raise PdfMergeError("error_compression_failed")

            shutil.copyfile(best_path, self.options.output_path)

    def _render_image_pdf(self, output_path: Path, dpi: int, jpeg_quality: int, fitz: object) -> None:
        source_doc = fitz.open(str(self.pdf_path))
        output_doc = fitz.open()
        zoom = dpi / 72
        matrix = fitz.Matrix(zoom, zoom)

        try:
            for source_page in source_doc:
                pixmap = source_page.get_pixmap(matrix=matrix, alpha=False, colorspace=fitz.csRGB)
                jpeg_bytes = pixmap.tobytes("jpeg", jpg_quality=jpeg_quality)
                output_page = output_doc.new_page(width=source_page.rect.width, height=source_page.rect.height)
                output_page.insert_image(output_page.rect, stream=jpeg_bytes)

            output_doc.save(str(output_path), garbage=4, deflate=True)
        finally:
            output_doc.close()
            source_doc.close()


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
