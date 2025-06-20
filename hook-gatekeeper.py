# Hook personnalisé pour PyInstaller pour le projet Gatekeeper
from PyInstaller.utils.hooks import collect_all, collect_data_files

# Collecter tous les modules du projet
datas = []
binaries = []
hiddenimports = []

# Modules du projet
project_modules = [
    'core',
    'ui',
    'mapping',
    'config',
]

for module in project_modules:
    module_datas, module_binaries, module_hiddenimports = collect_all(module)
    datas += module_datas
    binaries += module_binaries
    hiddenimports += module_hiddenimports

# Ajouter les imports cachés spécifiques
hiddenimports += [
    'core.anomalies',
    'core.ext_utils',
    'core.manual_review',
    'core.match_utils',
    'core.report',
    'core.rh_utils',
    'core.text_utils',
    'mapping.column_mapping',
    'mapping.directions_conservees',
    'mapping.profils_valides',
    'config.constants',
    'ui.main_window',
    'ui.pages.loading_page',
    'ui.pages.anomalies_page',
    'ui.pages.validation_page',
    'ui.pages.report_page',
    'ui.threads.processing_thread',
    'ui.widgets.stat_widget',
    'ui.widgets.file_drop_widget',
    'ui.styles',
    'ui.utils',
]

# S'assurer que les fichiers de données sont inclus
datas += [
    ('data/*.csv', 'data'),
    ('config/*.py', 'config'),
]