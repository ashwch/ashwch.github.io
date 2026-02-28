"""Markdown extension that prepends shared abbreviation definitions to every document."""

import os
import re

from markdown import Extension
from markdown.preprocessors import Preprocessor

ABBR_PATTERN = re.compile(r"^\*\[.+\]:")


class SharedAbbrPreprocessor(Preprocessor):
    """Appends abbreviation definitions from a shared file to every document."""

    def __init__(self, md, abbr_lines):
        super().__init__(md)
        self._abbr_lines = abbr_lines

    def run(self, lines):
        return lines + [""] + self._abbr_lines


class SharedAbbrExtension(Extension):
    """Registers the SharedAbbrPreprocessor, loading definitions once per build."""

    def __init__(self, **kwargs):
        self.config = {
            "file": ["", "Path to the shared abbreviations markdown file"],
        }
        super().__init__(**kwargs)
        self._abbr_lines = None

    def _load(self):
        path = self.getConfig("file")
        if not path or not os.path.isfile(path):
            self._abbr_lines = []
            return
        with open(path, encoding="utf-8") as f:
            self._abbr_lines = [
                line.rstrip() for line in f if ABBR_PATTERN.match(line)
            ]

    def extendMarkdown(self, md):
        if self._abbr_lines is None:
            self._load()
        md.registerExtension(self)
        md.preprocessors.register(
            SharedAbbrPreprocessor(md, self._abbr_lines),
            "shared_abbreviations",
            25,  # Before abbr extension (priority 12)
        )
