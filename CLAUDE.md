## 빌드

- Rust 확장은 maturin이 빌드 (`pyproject.toml`의 `[tool.maturin]` 참조)
- Wheel은 배포 워크플로우에서 생성되므로 로컬에서는 sdist만 빌드: `uv build --sdist`

## 테스트

```shell
uv run pytest ...
```

- 신규 테스트는 pytest 함수형으로 작성 (`test/test.py`는 업스트림 레거시 unittest이므로 예외)
