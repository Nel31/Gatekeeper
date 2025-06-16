# Modifications à apporter à Gatekeeper

## 1. Amélioration de l'algorithme de détection des changements de profil

### Problématique actuelle

L'algorithme actuel ne distingue pas deux cas de figure importants pour les changements de profil :

1. **Changement de poste réel** : L'utilisateur a effectivement changé de poste (ex: "Développeur" -> "Chef de projet")
2. **Écriture différente** : Le poste est le même mais écrit différemment (ex: "Développeur Python" vs "Développeur - Python")

### Solution proposée

#### 1.1 Modification de la structure de données

```python
# Nouvelle structure pour stocker les cas de changement de poste
CHANGEMENT_POSTE = {
    "changements_reels": {
        "code_utilisateur": {
            "ancien_poste": "profil_extraction",
            "nouveau_poste": "profil_rh",
            "date_changement": "date_validation",
            "certificateur": "certificateur"
        }
    },
    "ecritures_differentes": {
        "profil_extraction": {
            "profil_rh": "profil_rh_normalise",
            "date_validation": "date_validation",
            "certificateur": "certificateur"
        }
    }
}
```

#### 1.2 Modifications de l'algorithme

1. **Pour les changements de poste réels** :
   - Stocker l'historique des changements de poste par utilisateur
   - Permettre de consulter l'historique lors de la validation
   - Utiliser cet historique pour éviter de redemander une validation pour le même type de changement

2. **Pour les écritures différentes** :
   - Créer une table de correspondance entre les différentes écritures
   - Normaliser les profils lors de la comparaison
   - Stocker les correspondances validées pour les réutiliser

### Implémentation proposée

```python
def detecter_changement_profil(row, historique_changements, correspondances_profils):
    profil_ext = row.get('profil', '')
    profil_rh = row.get('profil_rh', '')
    
    # Vérifier si c'est un changement de poste connu
    if row['code_utilisateur'] in historique_changements:
        dernier_changement = historique_changements[row['code_utilisateur']][-1]
        if (dernier_changement['ancien_poste'] == profil_ext and 
            dernier_changement['nouveau_poste'] == profil_rh):
            return "changement_connu"
    
    # Vérifier si c'est une écriture différente connue
    if profil_ext in correspondances_profils:
        if correspondances_profils[profil_ext]['profil_rh'] == profil_rh:
            return "ecriture_connue"
    
    # Nouveau cas à valider
    return "a_valider"
```

## 2. Amélioration de l'algorithme de détection des changements de direction

### 2.1 Problématique actuelle

L'algorithme actuel présente les mêmes limitations pour les directions que pour les profils :

1. **Changement de direction réel** : L'utilisateur a effectivement changé de direction (ex: "Direction IT" -> "Direction Innovation")
2. **Écriture différente** : La direction est la même mais écrite différemment (ex: "Direction IT" vs "DIT" ou "Direction des Technologies de l'Information")

### 2.2 Solution proposée

#### 2.2.1 Modification de la structure de données

```python
# Nouvelle structure pour stocker les cas de changement de direction
CHANGEMENT_DIRECTION = {
    "changements_reels": {
        "code_utilisateur": {
            "ancienne_direction": "direction_extraction",
            "nouvelle_direction": "direction_rh",
            "date_changement": "date_validation",
            "certificateur": "certificateur"
        }
    },
    "ecritures_differentes": {
        "direction_extraction": {
            "direction_rh": "direction_rh_normalisee",
            "date_validation": "date_validation",
            "certificateur": "certificateur"
        }
    }
}
```

#### 2.2.2 Modifications de l'algorithme

1. **Pour les changements de direction réels** :
   - Stocker l'historique des changements de direction par utilisateur
   - Permettre de consulter l'historique lors de la validation
   - Utiliser cet historique pour éviter de redemander une validation pour le même type de changement

2. **Pour les écritures différentes** :
   - Créer une table de correspondance entre les différentes écritures de directions
   - Normaliser les directions lors de la comparaison
   - Stocker les correspondances validées pour les réutiliser

### 2.3 Implémentation proposée

```python
def detecter_changement_direction(row, historique_changements, correspondances_directions):
    direction_ext = row.get('direction', '')
    direction_rh = row.get('direction_rh', '')
    
    # Vérifier si c'est un changement de direction connu
    if row['code_utilisateur'] in historique_changements:
        dernier_changement = historique_changements[row['code_utilisateur']][-1]
        if (dernier_changement['ancienne_direction'] == direction_ext and 
            dernier_changement['nouvelle_direction'] == direction_rh):
            return "changement_connu"
    
    # Vérifier si c'est une écriture différente connue
    if direction_ext in correspondances_directions:
        if correspondances_directions[direction_ext]['direction_rh'] == direction_rh:
            return "ecriture_connue"
    
    # Nouveau cas à valider
    return "a_valider"
```

## 3. Amélioration de l'interface utilisateur

### 3.1 Problématique actuelle

- Double possibilité de prise de décision (tableau des anomalies et page de décisions manuelles)
- Risque de confusion pour l'utilisateur
- Possible incohérence dans les décisions

### 3.2 Solution proposée

#### 3.2.1 Simplification de l'interface

1. **Tableau des anomalies** :
   - Retirer les prises de décision
   - Garder uniquement l'affichage et le filtrage
   - Ajouter un bouton "Passer à la validation" pour chaque anomalie

2. **Page de décisions manuelles** :
   - Centraliser toutes les prises de décision
   - Ajouter un historique des décisions prises
   - Améliorer l'affichage des informations de contexte

#### 3.2.2 Nouvelle structure de l'interface

```text
[Tableau des anomalies]
  - Affichage des anomalies
  - Filtres et recherche
  - Bouton "Valider" pour chaque ligne
  - Pas de prise de décision directe

[Page de validation]
  - Affichage détaillé du cas
  - Historique des changements de poste
  - Correspondances de profils connues
  - Prise de décision
  - Commentaires et justifications
```

## 4. Plan d'implémentation

### Phase 1 : Amélioration de l'algorithme

1. Créer les nouvelles structures de données
2. Modifier l'algorithme de détection
3. Ajouter la gestion de l'historique
4. Implémenter la normalisation des profils

### Phase 2 : Refonte de l'interface

1. Retirer les prises de décision du tableau
2. Améliorer la page de validation
3. Ajouter l'historique et les correspondances
4. Tester la nouvelle interface

### Phase 3 : Tests et validation

1. Tests unitaires pour l'algorithme
2. Tests d'intégration
3. Tests utilisateurs
4. Validation des performances

## 5. Questions ouvertes

1. **Gestion de l'historique** :
   - Quelle durée de conservation pour l'historique des changements ?
   - Faut-il archiver les correspondances de profils ?

2. **Interface utilisateur** :
   - Comment gérer la transition pour les utilisateurs habitués à l'ancienne interface ?
   - Faut-il garder une option de prise de décision rapide pour les cas simples ?

3. **Performance** :
   - Impact de l'historique sur les performances ?
   - Optimisation de la recherche dans les correspondances ?
