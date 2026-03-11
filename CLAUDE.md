## 빌드

- Rust 확장은 maturin이 빌드 (`pyproject.toml`의 `[tool.maturin]` 참조)
- 개발 중 Rust 확장 빌드: `uv run maturin develop --uv --release` (`--uv` 필수, `--release` 생략 시 debug 빌드로 성능 측정이 부정확)
- Wheel은 배포 워크플로우에서 생성되므로 로컬에서는 sdist만 빌드: `uv build --sdist`

## 테스트

```shell
uv run pytest ...
```

- 신규 테스트는 pytest 함수형으로 작성 (`test/test.py`는 업스트림 레거시 unittest이므로 예외)

## 에러 메시지

- 포맷팅: f-string (동적 값 없으면 일반 문자열)
- 코드 식별자(파라미터명, 메서드명 등): 작은따옴표로 감싸고 소문자 유지
- 첫 글자: 대문자 (단, 작은따옴표로 시작하는 경우 제외)
- 축약형: 미사용 (`cannot`, `could not`)
- 마침표: 없음

## README

- 영어로 작성
- upstream과 외부 동작이 달라지는 변경(API 삭제, 동작 변경, 새 기능 등)은 `README.md`의 "Changes from Upstream" 섹션에 반드시 반영
