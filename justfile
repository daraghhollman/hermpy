build:
    uv run make --directory ./docs/ clean
    uv run make --directory ./docs/ html

serve:
    xdg-open ./docs/build/html/index.html
