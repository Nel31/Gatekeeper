"""
Helper pour ajouter automatiquement des tooltips aux cellules tronquées
"""

from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt6.QtGui import QFontMetrics


class TableTooltipHelper:
    """Helper pour gérer les tooltips automatiques dans les tableaux"""
    
    @staticmethod
    def setup_tooltips_for_table(table: QTableWidget):
        """
        Configurer les tooltips automatiques pour un tableau
        
        Args:
            table: Le QTableWidget à configurer
        """
        # Connecter aux événements de redimensionnement
        table.horizontalHeader().sectionResized.connect(
            lambda: TableTooltipHelper.update_all_tooltips(table)
        )
        
        # Mettre à jour les tooltips initiaux
        TableTooltipHelper.update_all_tooltips(table)
    
    @staticmethod
    def update_all_tooltips(table: QTableWidget):
        """Mettre à jour tous les tooltips du tableau"""
        for row in range(table.rowCount()):
            for col in range(table.columnCount()):
                TableTooltipHelper.update_cell_tooltip(table, row, col)
    
    @staticmethod
    def update_cell_tooltip(table: QTableWidget, row: int, col: int):
        """
        Mettre à jour le tooltip d'une cellule spécifique
        
        Args:
            table: Le QTableWidget
            row: Index de la ligne
            col: Index de la colonne
        """
        item = table.item(row, col)
        if not item:
            return
        
        text = item.text()
        if not text:
            return
        
        # Calculer si le texte est tronqué
        column_width = table.columnWidth(col)
        font_metrics = QFontMetrics(item.font())
        text_width = font_metrics.horizontalAdvance(text)
        
        # Marges et padding approximatifs
        padding = 16  # Ajuster selon votre style
        
        # Si le texte déborde, ajouter le tooltip
        if text_width > (column_width - padding):
            item.setToolTip(text)
        else:
            item.setToolTip("")  # Retirer le tooltip si plus nécessaire
    
    @staticmethod
    def create_item_with_tooltip(text: str, table: QTableWidget, col: int):
        """
        Créer un QTableWidgetItem avec tooltip automatique
        
        Args:
            text: Le texte de l'item
            table: Le tableau parent
            col: L'index de la colonne
            
        Returns:
            QTableWidgetItem configuré
        """
        item = QTableWidgetItem(text)
        
        # Vérifier immédiatement si tooltip nécessaire
        column_width = table.columnWidth(col)
        font_metrics = QFontMetrics(item.font())
        text_width = font_metrics.horizontalAdvance(text)
        
        if text_width > (column_width - 16):
            item.setToolTip(text)
        
        return item 