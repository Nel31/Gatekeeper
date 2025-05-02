# GatekeeperPipeline

## Description
`GatekeeperPipeline` est un algorithme conçu pour automatiser la revue et la certification des comptes utilisateurs applicatifs en entreprise. Il compare les extractions de comptes avec le référentiel RH, détecte les anomalies, gère les doublons, et génère un rapport final au format Excel. En option, il peut envoyer par mail les fichiers de certification pour les prestataires externes.

## Prérequis
- Python 3.6 ou supérieur
- Bibliothèques Python :
  - pandas
  - openpyxl
  - python-dateutil
  - fuzzywuzzy (pour le fuzzy matching)
  - pywin32 (pour l’intégration Outlook sous Windows)

## Installation
```bash
pip install pandas openpyxl python-dateutil fuzzywuzzy pywin32
```

## Usage
```bash
python gatekeeper_pipeline.py \
  --rh-file RH.xlsx \
  --ext-file extraction.xlsx \
  --template template_revue.xlsx \
  --output rapport_revue.xlsx \
  --certificateur "Jean Dupont" \
  [--email-list mails.txt] \
  [--only-insgb] [--only-outsgb] [--use-outlook]
```

### Arguments
| Option                | Description                                                                                      |
|-----------------------|--------------------------------------------------------------------------------------------------|
| `--rh-file`           | Chemin vers le fichier Excel du référentiel RH                                                   |
| `--ext-file`          | Chemin vers le fichier Excel d’extraction applicative                                            |
| `--template`          | Chemin vers le template Excel de revue                                                           |
| `--output`            | Chemin de sortie pour le fichier Excel de revue final                                            |
| `--certificateur`     | Nom du certificateur devant être inscrit dans le rapport                                         |
| `--email-list`        | (Optionnel) Chemin vers un fichier TXT contenant les adresses mail des prestataires externes      |
| `--only-insgb`        | (Flag) Génère uniquement la partie interne (agents SGB)                                           |
| `--only-outsgb`       | (Flag) Génère uniquement la partie externe (agents hors SGB)                                      |
| `--use-outlook`       | (Flag) Active l’envoi automatique des mails via Outlook                                          |

## Étapes de l’algorithme
1. **Chargement & validation**
   - Lecture des fichiers Excel RH et extraction.
   - Normalisation et validation des en-têtes.
2. **Nettoyage & filtrage**
   - Uniformisation des textes (`lib`, `lputi`, `status`).
   - Conversion des dates.
   - Filtrage des comptes suspendus.
3. **Agrégation & détection d’anomalies**
   - Agrégation par utilisateur (`cuti`) pour déterminer la dernière connexion, anomalies de libellés et statuts.
4. **Fusion RH ↔ extraction**
   - Jointure gauche entre l’extraction agrégée et le référentiel RH.
   - Catégorisation des comptes en internes (`in_sgb`) ou externes (`out_sgb`).
   - Calcul des jours d’inactivité.
5. **Détection des doublons**
   - Vérification des doublons de noms/prénoms pour les comptes internes. En cas de doublons, interruption du processus (exit code 84).
6. **Construction du rapport**
   - Génération des lignes du rapport avec décisions et exécutions automatiques pour les internes.
   - Attribution manuelle pour les externes.
7. **Injection dans le template Excel**
   - Remplissage du template ligne par ligne.
8. **Flux mail Out SGB (optionnel)**
   - Envoi des certificats Excel aux prestataires externes via Outlook.

## Structure du rapport
| Colonne                  | Description                                                   |
|--------------------------|---------------------------------------------------------------|
| `code_utilisateur`       | Identifiant du compte (`cuti`)                                |
| `nom_prenom`             | Nom et prénom de l’utilisateur                                |
| `profil`                 | Poste ou profil RH                                            |
| `direction`              | Direction ou service                                          |
| `recommandation`         | Valeur par défaut : `A certifier`                             |
| `commentaire_revue`      | Commentaires éventuels de la revue                            |
| `certificateur`          | Nom du certificateur                                          |
| `décision`               | Décision finale (`A conserver`, `A désactiver`, etc.)        |
| `exécution`              | Résultat de l’exécution (`Conservé`, `Désactivé`, `Modifié`)  |
| `exécuté_par`            | Nom de l’opérateur ayant réalisé l’exécution                  |
| `commentaire_exécution`  | Commentaires éventuels sur l’exécution                        |

## Exemple d’exécution
```bash
python gatekeeper_pipeline.py --rh-file RH.xlsx --ext-file ext.xlsx --template template.xlsx \
  --output rapport.xlsx --certificateur "Alice Martin" --use-outlook
```

## Licence
MIT
