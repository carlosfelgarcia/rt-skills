# Tests: pipeline

The pytest forms of the rules in `rules/test.md`.

- **Empty values** for the gutted check: `None`, `[]`, `""`, `0`.

## The five shapes

- **Weak or no assertion.** `assert result`, `assert x is not None`, `assert isinstance(x, Foo)`, `assert len(x) > 0`.
- **Mock or absence only.** `mock.assert_called()`, `mock.assert_not_called()`, `assert x is None`, `assert result == []`, `assert len(result) == 0`, `assert x != wrong`.
- **Self-referential.** `assert f(a) == f(a)`, `assert parsed.url == build_url(...)`.
- **Constant pin.** `assert LIMITS["max_tools"] == 8`, `assert "You are" in PROMPT`.
- **Fixture asserts fixture.** A value computed in a `@pytest.fixture` or `setUp`.

**The fix**, for example: `assert slugify("Hello, World!") == "hello-world"`.

**Keep** a type-level check that mypy or pyright runs rather than pytest, such as `typing.assert_type`.
