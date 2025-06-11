"""
Package pages pour les différentes étapes de l'application
"""

from .loading_page import LoadingPage
from .anomalies_page import AnomaliesPage
from .validation_page import ValidationPage
from .report_page import ReportPage

__all__ = ['LoadingPage', 'AnomaliesPage', 'ValidationPage', 'ReportPage']