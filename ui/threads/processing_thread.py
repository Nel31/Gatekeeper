"""
Thread pour le traitement des données en arrière-plan
"""

from PyQt6.QtCore import QThread, pyqtSignal

# Import des modules existants
from core.rh_utils import charger_et_preparer_rh
from core.ext_utils import charger_et_preparer_ext
from core.match_utils import associer_rh_aux_utilisateurs
from core.anomalies import detecter_anomalies


class ProcessingThread(QThread):
    """Thread pour le traitement des données"""
    
    progress = pyqtSignal(str)
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    
    def __init__(self, rh_paths, ext_path, certificateur):
        super().__init__()
        self.rh_paths = rh_paths
        self.ext_path = ext_path
        self.certificateur = certificateur
    
    def run(self):
        """Exécuter le traitement des données"""
        try:
            self.progress.emit("Chargement des fichiers RH...")
            rh_df = charger_et_preparer_rh(self.rh_paths)
            
            self.progress.emit("Chargement du fichier d'extraction...")
            ext_df = charger_et_preparer_ext(self.ext_path)
            
            self.progress.emit("Association des données RH...")
            ext_df = associer_rh_aux_utilisateurs(ext_df, rh_df)
            
            self.progress.emit("Détection des anomalies...")
            ext_df = detecter_anomalies(ext_df, certificateur=self.certificateur)
            
            self.progress.emit("Traitement terminé!")
            self.finished.emit(ext_df)
            
        except Exception as e:
            self.error.emit(str(e))