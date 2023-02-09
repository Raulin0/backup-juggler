import os
from pathlib import Path

from tqdm import tqdm


class JugglerModel:
    def __init__(self, source, destination):
        self._source = Path(source)
        self._destination = Path(destination)

        if self.source.is_file():
            self._total_size = self.source.stat().st_size
        else:
            total_size = 0
            for src_file in self.source.rglob('*.*'):
                total_size += src_file.stat().st_size
            self._total_size = total_size

    @property
    def source(self):
        return self._source

    @property
    def destination(self):
        return self._destination

    @property
    def total_size(self):
        return self._total_size


class JugglerView:
    def __init__(self, model):
        self._pbar = tqdm(
            total=model.total_size,
            unit='B',
            unit_scale=True,
            desc=f'Copying {model.source} to {model.destination}',
        )

    @property
    def pbar(self):
        return self._pbar

    def update(self, chunk_size):
        self._pbar.update(chunk_size)


class JugglerController:
    def __init__(self, model, view):
        self._model = model
        self._view = view

    def do_copy(self):
        self._copy_to()

    def _copy_to(self):
        if self._model.source.is_file():
            with self._view.pbar:
                src_file = self._model.source
                dst_file = (
                    self._model.destination / src_file.stem / src_file.name
                )
                dst_file.parent.mkdir(parents=True, exist_ok=True)
                self._copy_file(src_file, dst_file)
        else:
            with self._view.pbar:
                for src_file in self._model.source.rglob('*.*'):
                    dst_file = (
                        self._model.destination
                        / self._model.source.stem
                        / src_file.relative_to(self._model.source)
                    )
                    dst_file.parent.mkdir(parents=True, exist_ok=True)
                    self._copy_file(src_file, dst_file)

    def _copy_file(self, src_file, dst_file):
        with open(src_file, 'rb') as src, open(dst_file, 'wb') as dst:
            while True:
                chunk = src.read(1024 * 1024)
                if not chunk:
                    break
                dst.write(chunk)
                self._view.update(len(chunk))
        os.utime(
            dst_file, (src_file.stat().st_atime, src_file.stat().st_mtime)
        )
        os.chmod(dst_file, src_file.stat().st_mode)
