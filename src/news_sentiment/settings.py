from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectPaths:
    root: Path

    @property
    def data_dir(self) -> Path:
        return self.root / "data"

    @classmethod
    def discover(cls, cwd: Path | None = None) -> "ProjectPaths":
        return cls(root=(cwd or Path.cwd()))
