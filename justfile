default:
    just -l

docs-build:
    uv run make --directory ./docs/ clean
    uv run make --directory ./docs/ html

docs-quick-build:
    uv run make --directory ./docs/ clean
    SPHINX_EXEC_CODE_SKIP=1 uv run make --directory ./docs/ html

docs-serve:
    $BROWSER ./docs/build/html/index.html
