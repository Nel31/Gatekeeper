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
1. ── CHARGEMENT & VALIDATION ─────────────────────────────────────────────────
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

2. ── NETTOYAGE & FILTRAGE ────────────────────────────────────────────────────
   FOR each col IN {lib, lputi, status} DO
       ext_df[col] ← to_lower(strip(unidecode(ext_df[col])))
       // Uniformiser le texte et supprimer accents
   END FOR

   ext_df.last_login      ← PARSE_DATE(ext_df.last_login)
       // Convertir en date
   ext_df.extraction_date ← PARSE_DATE(ext_df.extraction_date)

   ext_df ← FILTER ext_df WHERE status ≠ 'suspendu'
       // Retirer les comptes suspendus

3. ── AGRÉGATION & ANOMALIES ─────────────────────────────────────────────────
   summary_df ← GROUP ext_df BY cuti:
       last_login      = MAX(last_login)
           // Date de dernière connexion la plus récente
       extraction_date = FIRST(extraction_date)
           // Date d’extraction unique
       lib_anomaly     = (COUNT_UNIQUE(lib) > 1)
           // Plusieurs libellés différents ?
       lputi_extracted = FIRST(lputi)
           // Conserver le premier intitulé métier
       lputi_anomaly   = (COUNT_UNIQUE(lputi) > 1)
           // Anomalie sur l’intitulé métier ?
       status_anomaly  = (COUNT_UNIQUE(status) > 1)
           // Anomalie sur le statut ?
   END GROUP

4. ── FUSION RH ↔ EXT ────────────────────────────────────────────────────────
   merged ← LEFT_MERGE(summary_df, rh_df, on=(cuti = rh_id), indicator=_merge)
       // Conserver tous les comptes, marquer In/Out SGB

   FOR each row IN merged DO
       IF row._merge = 'both' THEN
           row.category ← 'in_sgb'
       ELSE
           row.category ← 'out_sgb'
       END IF

       // Calcul du nombre de jours d’inactivité
       IF row.last_login IS NULL THEN
           row.days_inactive ← +∞   // Jamais utilisé
       ELSE
           row.days_inactive ← DAYS_BETWEEN(row.extraction_date, row.last_login)
       END IF
   END FOR

5. ── DÉTECTION DES DOUBLONS ─────────────────────────────────────────────────
   in_sgb_rows ← FILTER merged WHERE category = 'in_sgb'
   full_names  ← [r.last_name + " " + r.first_name FOR r IN in_sgb_rows]
   IF ANY DUPLICATE(full_names) THEN
       PRINT "Doublons détectés" AND EXIT(84)
       // Arrêt si un même collaborateur a plusieurs comptes
   END IF

6. ── CONSTRUCTION DU RAPPORT ────────────────────────────────────────────────
   report_rows ← EMPTY LIST

   FOR each row IN merged DO
       // Initialisation des champs
       code_utilisateur      ← row.cuti
       nom_prenom            ← ""
       profil                ← ""
       direction             ← ""
       recommandation        ← "A certifier"
       commentaire_revue     ← ""
       certificateur_field   ← certificateur
       décision              ← ""
       exécution             ← ""
       exécuté_par           ← ""
       commentaire_exécution ← ""

       IF row.category = 'in_sgb' THEN
           // Données RH pour les internes
           nom_prenom ← row.last_name + " " + row.first_name
           profil     ← row.position
           direction  ← row.direction

           // Décision automatique
           IF row.days_inactive > SETTINGS.threshold_days_inactive THEN
               décision = "A désactiver"
           ELSE
               décision = "A conserver"
           END IF

           // Exécution priorise la désactivation
           IF décision = "A désactiver" THEN
               exécution = "Désactivé"
           ELSE
               // Fuzzy-match profil vs extrait
               score ← FUZZY_SCORE(profil, row.lputi_extracted)
               IF score < 85 THEN
                   exécution = "Modifié"
               ELSE
                   exécution = "Conservé"
               END IF
           END IF
       END IF
       // Pour out_sgb, décision/exécution restent vides (manuel)

       APPEND to report_rows:
           (code_utilisateur, nom_prenom, profil, direction,
            recommandation, commentaire_revue, certificateur_field,
            décision, exécution, exécuté_par, commentaire_exécution)
   END FOR

   report_df ← DATAFRAME(report_rows, columns=[
       code_utilisateur, nom_prenom, profil, direction,
       recommandation, commentaire_revue, certificateur,
       décision, exécution, exécuté_par, commentaire_exécution
   ])

7. ── INJECTION DANS LE TEMPLATE EXCEL ───────────────────────────────────────
   wb ← LOAD_WORKBOOK(template_path)
   ws ← wb.active
   header_map ← {NORMALIZE(cell.value): cell.column FOR cell IN ws[1]}

   FOR i FROM 0 TO report_df.ROWS – 1 DO
       FOR each (col_name, value) IN report_df.row(i) DO
           hdr ← TEMPLATE_HEADER[col_name]
           col_index ← header_map[NORMALIZE(hdr)]
           ws.cell(row=i+2, column=col_index, value=value)
       END FOR
   END FOR
   wb.save(output_path)
       // Rapport final prêt

8. ── FLUX MAIL OUT SGB (optionnel) ─────────────────────────────────────────
   IF do_outsgb AND email_list IS PROVIDED THEN
       addresses ← READ_LINES(email_list)
       OUTLOOK ← INIT_OUTLOOK_COM()
       FOR each addr IN addresses DO
           mail ← OUTLOOK.CreateItem()
           mail.To      ← addr
           mail.Subject ← "Validation comptes externes – " + certificateur
           mail.Body    ← <<message standard>>

           attachment_path ← PATH_JOIN("outsgb", addr + ".xlsx")
           mail.Attachments.Add(attachment_path)
               // Pièce jointe automatique

           TRY
               mail.Send()
               status, error ← "Succès", ""
           CATCH e
               status, error ← "Échec", e.message
           END TRY

           LOG_SEND_RESULT(addr, status, error)
               // Journalisation dans outlook_send_log.csv
       END FOR
   END IF

END ALGORITHM
