"""
Configuration constants - Remplace les fichiers YAML
"""

# Mapping des alias de colonnes (remplace column_aliases.yml)
COLUMN_ALIASES = {
    'code_utilisateur': [
        'Identifiant',
        'Identifiant Local',
        'CODE_UTILISATEUR',
        'CUTI',
        'UTICOD',
        'Code utilisateur',
        'Identifiant utilisateur'
    ],

    'nom_prenom': [
        'NomComplet',
        'Nom et Prénoms',
        'Nom de Famille',
        'Prénom(s)',
        'NOM_UTILISATEUR',
        'LIB',
        'Nom et Prénoms utilisateur',
        'Nom et Prénom',
        'NOMU',
        'UTINOM'
    ],

    'profil': [
        'Profil utilisateur',
        'Intitulé du poste',
        'PROFIL',
        'LPUTI',
        'LPRO',
        'PROFCOD',
        'position',
        'Intitule de poste',
        'profil'
    ],

    'direction': [
        'LBSER',
        'Direction',
        'LSER',
        'Libelle service',
        'LIBELLE SERVICE'
    ],

    'last_login': [
        'DateDerniereModif',
        'DATE_DERNIÈRE_CONNEXION',
        'date_de_derniere_connexion',
        'DATE DE DERNIERE CONNEXION'
    ],

    'status': [
        'ACTI',
        'ACTIF',
        'Statut du compte Suspendu',
        'SUS',
        'SUSP',
        'SUSPENDU',
        'SS'
    ],

    'extraction_date': [
        'DATE_EXTRACTION'
    ]
}

# Paramètres de configuration (remplace params.yml)
CONFIG_PARAMS = {
    # Seuils de détection
    'thresholds': {
        # Seuil de similarité pour le fuzzy matching (0-100)
        'similarity': 85,

        # Nombre de jours d'inactivité avant désactivation automatique
        'inactivity_days': 120
    },

    # Règles de décision automatique
    'auto_decisions': {
        # Décision pour les comptes inactifs
        'inactive_accounts': "Désactiver",

        # Décision pour les profils/directions whitelistés
        'whitelisted_changes': "Conserver",

        # Décision pour les fuzzy matches validés
        'fuzzy_matches': None  # Pas de décision, juste validation
    },

    # Messages et labels
    'messages': {
        # Messages d'anomalies
        'anomalies': {
            'non_rh': "Compte non RH",
            'profile_change': "Changement de profil à vérifier",
            'direction_change': "Changement de direction à vérifier",
            'inactive': "Compte potentiellement inactif"
        },

        # Labels de décision pour le rapport
        'decision_labels': {
            'Conserver': {
                'decision': "A conserver",
                'execution': "Conservé"
            },
            'Modifier': {
                'decision': "A Modifier",
                'execution': "Modifié"
            },
            'Désactiver': {
                'decision': "A desactiver",
                'execution': "Désactivé"
            }
        }
    },

    # Options d'affichage
    'display': {
        # Couleurs pour les décisions (format hex)
        'colors': {
            'Conserver': "#4caf50",
            'Modifier': "#ff9800",
            'Désactiver': "#f44336"
        },

        # Nombre maximum de lignes dans l'aperçu du rapport
        'max_preview_rows': 100,

        # Afficher les cas automatiques dans un onglet séparé
        'separate_auto_cases': True
    },

    # Logging et audit
    'logging': {
        # Logger les cas automatiques dans la console
        'log_auto_cases': True,

        # Niveau de détail (DEBUG, INFO, WARNING, ERROR)
        'level': "INFO",

        # Sauvegarder un log des décisions
        'save_decision_log': True,
        'log_file': "decisions.log"
    },

    # Export
    'export': {
        # Formats disponibles pour l'export
        'formats': ["xlsx", "csv"],

        # Inclure un résumé dans le rapport
        'include_summary': True,

        # Ajouter la date/heure dans le nom du fichier
        'timestamp_filename': True
    }
}