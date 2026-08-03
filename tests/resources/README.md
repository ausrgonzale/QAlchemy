# Test Resources

This directory contains reusable resources shared by the QAlchemy test suite.

Guidelines:

- Resources should be read-only.
- Do not modify resource files during tests.
- Tests requiring writable files should copy resources into `tmp_path`.
- Keep resources intentionally minimal while remaining structurally valid.