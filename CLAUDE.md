## 빌드

- Cython `.pyx` 파일 수정 시, 생성된 `.c` 파일도 함께 커밋
- C 코드 재생성: `uv build --sdist`
- Wheel은 배포 워크플로우에서 생성되므로 로컬에서는 sdist만 빌드

## 테스트

```shell
uv run pytest ...
```

- 신규 테스트는 pytest 함수형으로 작성 (`test/test.py`는 업스트림 레거시 unittest이므로 예외)
