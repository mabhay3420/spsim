## Run and Test

1. Install uv

```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Setup environment
```
uv sync --python-preference=only-managed 
```
3. Activate environment
```
source .venv/bin/activate
```

4. Run End 2 End
```
uv run scripts/run.py
``` 

Run end 2 end with fresh data
```
uv run scripts/run.py --refresh
```

5. Run tests

Install editable project
```
uv pip install -e .
```
Run pytest
```
pytest -q

```

## Styling instructions
1. To add new dependencies use:
```
uv add <package>
```

2. Always use types.

3. Write tests for each function you add.

4. Try to keep functions small and focused and avoid side effects.

5. Format code with:
```
ruff format
```