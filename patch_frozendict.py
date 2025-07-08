from pathlib import Path
import re

path = Path("venv/lib/python3.12/site-packages/frozendict/__init__.py")
code = path.read_text()
code = re.sub(r"from collections import Mapping", "from collections.abc import Mapping", code)
path.write_text(code)