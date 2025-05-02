# Gatekeeper Pipeline (version simplifiée)

Ce document présente la version simplifiée de l'algorithme Gatekeeper en pseudocode.

```plaintext
ALGORITHME GatekeeperSimplifié
ENTRÉES :
  - rh_file       : chemin vers le fichier Excel RH
  - ext_file      : chemin vers le fichier Excel d’extraction
  - template_file : chemin vers le template Excel
  - output_file   : chemin pour le rapport final
  - certificateur : nom du certificateur

DÉBUT

1. CHARGER LES DONNÉES
   rh_df  ← lire_excel(rh_file)    // Référentiel RH
   ext_df ← lire_excel(ext_file)   // Extraction applicative

2. VALIDER ET RENOMMER LES COLONNES
   pour chaque colonne de rh_df et ext_df :
     normaliser le nom (minuscules, supprimer espaces et accents)
     renommer selon la liste d’alias
   SI une colonne attendue est manquante :
     ERREUR et arrêt

3. NETTOYER ext_df
   transformer les textes en minuscules sans accents
   convertir last_login et extraction_date en dates
   supprimer les comptes suspendus

4. AGRÉGER PAR UTILISATEUR
   regrouper ext_df par cuti et calculer :
     - last_login max
     - extraction_date premier
     - indicateurs d’anomalie (libellé, métier, statut)

5. APPARIER RH ↔ EXT
   merged ← fusion gauche de l’agrégation avec rh_df
     si trouvé dans RH → catégorie = InSGB
     sinon             → catégorie = OutSGB
   calculer days_inactive = extraction_date – last_login (ou infini si absent)

6. VÉRIFIER LES DOUBLONS
   pour chaque ligne InSGB :
     construire nom complet = last_name + " " + first_name
   SI un nom complet apparaît plusieurs fois :
     ERREUR et arrêt

7. PRÉPARER LE RAPPORT
   initialiser une liste vide report_rows
   pour chaque ligne de merged :
     remplir les champs :
       code_utilisateur, nom_prenom (InSGB), profil (InSGB), direction (InSGB),
       recommandation = "A certifier",
       certificateur,
       décision/exécution calculées pour InSGB, vides pour OutSGB
   report_df ← tableau de report_rows avec colonnes dans l’ordre du template

8. ÉCRIRE DANS LE TEMPLATE
   ouvrir template_file
   pour chaque ligne de report_df :
     écrire les valeurs sous les bonnes en-têtes
   sauvegarder sous output_file

FIN
```
