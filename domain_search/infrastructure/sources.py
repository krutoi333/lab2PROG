# Чтение текста и файлов с ограничением размера.

from dataclasses import dataclass
from pathlib import Path

from domain_search.application.search import Source, SourceError

MAX_BYTES = 5 * 1024 * 1024


@dataclass(frozen=True)
class StringSource(Source):
    text: str

    def read(self) -> str:
        return self.text


@dataclass(frozen=True)
class FileSource(Source):
    path: Path
    encoding: str = "utf-8-sig"

    def read(self) -> str:
        data = self._read_bytes()
        return _decode_text(data, self.encoding)

    def _read_bytes(self) -> bytes:
        try:
            with self.path.open("rb") as stream:
                return stream.read(MAX_BYTES + 1)
        except OSError as error:
            raise SourceError(f"Не удалось прочитать файл: {error}") from error


def _decode_text(data: bytes, encoding: str) -> str:
    # Проверяет размер до декодирования, в том числе для многобайтного текста.
    if len(data) > MAX_BYTES:
        raise SourceError(f"Размер источника превышает {MAX_BYTES} байт.")
    try:
        return data.decode(encoding)
    except (LookupError, UnicodeError) as error:
        raise SourceError(f"Не удалось декодировать текст: {error}") from error
