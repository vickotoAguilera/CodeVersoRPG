import importlib.util
from pathlib import Path
import traceback

path = Path('editor_unificado.py').resolve()
print('Loading from path:', path)
try:
    spec = importlib.util.spec_from_file_location('editor_unificado_mod', str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    print('LOADED_OK:', hasattr(module, 'EditorUnificado'))
except Exception:
    traceback.print_exc()
