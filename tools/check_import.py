import importlib
import traceback

try:
    m = importlib.import_module('editor_unificado')
    print('IMPORT_OK:', hasattr(m, 'EditorUnificado'))
except Exception:
    traceback.print_exc()
