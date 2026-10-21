# Contributing

Please contribute by proposing a merger request.

You can install the project in development mode like so:
```sh
git clone https://github.com/meteofrance/calendardataviz.git
cd calendardataviz
uv sync --all-extras
```

To format, type check then test your code:
```
uv run ruff format
uv run ruff check --fix
uv run pyright
uv run pytest -s
```

Once your code is formated and tested, you can create a merge request
of your branch into the main branch.
