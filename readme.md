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
ALGORITHM GatekeeperPipeline
INPUT:
    rh_file            // chemin vers le fichier Excel RH
    ext_file           // chemin vers le fichier Excel d’extraction
    template_path      // chemin vers le template Excel de revue
    output_path        // chemin pour le fichier Excel de revue final
    certificateur      // nom du certificateur
    email_list (opt.)  // chemin vers le fichier TXT d’adresses mail
    flags: { only_insgb, only_outsgb, use_outlook }

BEGIN
1. ── CHARGEMENT & VALIDATION ─────────────────────────────────────────────
   1.1 rh_df ← READ_EXCEL(rh_file)
       // Charger le référentiel RH

   1.2 ext_df ← READ_EXCEL(ext_file)
       // Charger l’extraction applicative

   1.3 CALL validate_rh_dataframe(rh_df)
       ▸ Normaliser les entêtes (unidecode + minuscules + suppression non alphanum)
       ▸ Renommer selon les alias RH attendus
       ▸ ERREUR si colonnes manquantes

   1.4 CALL validate_dataframe(ext_df)
       ▸ Normaliser les entêtes de la même manière
       ▸ Renommer selon les alias d’extraction attendus
       ▸ ERREUR si colonnes manquantes

2. ── NETTOYAGE & FILTRAGE ────────────────────────────────────────────────
   FOR each col IN {lib, lputi, status} DO
       ext_df[col] ← to_lower(strip(unidecode(ext_df[col])));
   END FOR

   ext_df.last_login      ← PARSE_DATE(ext_df.last_login)
   ext_df.extraction_date ← PARSE_DATE(ext_df.extraction_date)

   ext_df ← FILTER ext_df WHERE status ≠ 'suspendu'

3. ── AGRÉGATION & ANOMALIES ───────────────────────────────────────────────
   summary_df ← GROUP ext_df BY cuti:
       last_login      = MAX(last_login)
       extraction_date = FIRST(extraction_date)
       lib_anomaly     = (COUNT_UNIQUE(lib) > 1)
       lputi_extracted = FIRST(lputi)
       lputi_anomaly   = (COUNT_UNIQUE(lputi) > 1)
       status_anomaly  = (COUNT_UNIQUE(status) > 1)
   END GROUP

4. ── FUSION RH ↔ EXT ─────────────────────────────────────────────────────
   merged ← LEFT_MERGE(summary_df, rh_df, on=(cuti = rh_id), indicator=_merge)

   FOR each row IN merged DO
       IF row._merge = 'both' THEN
           row.category ← 'in_sgb'
       ELSE
           row.category ← 'out_sgb'
       END IF

       IF row.last_login IS NULL THEN
           row.days_inactive ← +∞
       ELSE
           row.days_inactive ← DAYS_BETWEEN(row.extraction_date, row.last_login)
       END IF
   END FOR

5. ── DÉTECTION DES DOUBLONS ───────────────────────────────────────────────
   in_sgb_rows ← FILTER merged WHERE category = 'in_sgb'
   IF ANY DUPLICATE([r.last_name + " " + r.first_name FOR r IN in_sgb_rows]) THEN
       PRINT "Doublons détectés" AND EXIT(84)
   END IF

6. ── CONSTRUCTION DU RAPPORT ───────────────────────────────────────────────
   report_rows ← EMPTY LIST

   FOR each row IN merged DO
       INITIALISE les champs du rapport

       IF row.category = 'in_sgb' THEN
           // Données RH pour internes
           SET nom_prenom, profil, direction

           // Décision automatique
           IF row.days_inactive > SETTINGS.threshold_days_inactive THEN
               décision = "A désactiver"
           ELSE
               décision = "A conserver"
           END IF

           // Exécution
           IF décision = "A désactiver" THEN
               exécution = "Désactivé"
           ELSE
               score ← FUZZY_SCORE(profil, row.lputi_extracted)
               IF score < 85 THEN
                   exécution = "Modifié"
               ELSE
                   exécution = "Conservé"
               END IF
           END IF
       END IF

       APPEND to report_rows
   END FOR

7. ── INJECTION DANS LE TEMPLATE EXCEL ─────────────────────────────────────
   wb ← LOAD_WORKBOOK(template_path)
   ws ← wb.active
   header_map ← {NORMALIZE(cell.value): cell.column FOR cell IN ws[1]}

   FOR i FROM 0 TO report_df.ROWS – 1 DO
       WRITE chaque valeur du report_df dans la cellule correspondante
   END FOR

   wb.save(output_path)

8. ── FLUX MAIL OUT SGB (optionnel) ────────────────────────────────────────
   IF do_outsgb AND email_list IS PROVIDED THEN
       POUR chaque adresse DANS email_list:
           CRÉER et ENVOYER un mail Outlook avec pièce jointe
   END IF

END ALGORITHM
