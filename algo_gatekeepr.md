<span class="kw">ALGORITHM</span> GatekeeperPipeline
<span class="kw">INPUT</span>:
    <span class="value">rh_file</span>            // chemin vers le fichier Excel RH
    <span class="value">ext_file</span>           // chemin vers l’extraction applicative
    <span class="value">template_path</span>      // chemin vers le template Excel de revue
    <span class="value">output_path</span>        // chemin pour le fichier Excel final
    <span class="value">certificateur</span>      // nom du certificateur
    <span class="value">email_list</span> (opt.)  // fichier TXT d’adresses mail
    <span class="value">flags</span>              // { only_insgb, only_outsgb, use_outlook }

<span class="kw">BEGIN</span>

1. ── <span class="kw">CHARGEMENT & VALIDATION</span> ─────────────────────────────────
   1.1 rh_df ← READ_EXCEL(rh_file)  <span class="comment">// Charger le référentiel RH</span>
   1.2 ext_df ← READ_EXCEL(ext_file) <span class="comment">// Charger l’extraction</span>

   1.3 CALL validate_rh_dataframe(rh_df)
       ▸ Normaliser entêtes (unidecode + minuscules + suppression non alphanum)
       ▸ Renommer selon les alias RH attendus
       ▸ ERREUR si colonnes manquantes

   1.4 CALL validate_dataframe(ext_df)
       ▸ Normaliser entêtes
       ▸ Renommer selon les alias d’extraction
       ▸ ERREUR si colonnes manquantes

2. ── <span class="kw">NETTOYAGE & FILTRAGE</span> ─────────────────────────────────
   <span class="kw">FOR</span> each col IN {lib, lputi, status} <span class="kw">DO</span>
       ext_df[col] ← to_lower(strip(unidecode(ext_df[col])))  <span class="comment">// Uniformiser texte</span>
   <span class="kw">END FOR</span>

   ext_df.last_login      ← PARSE_DATE(ext_df.last_login)      <span class="comment">// Convertir en date</span>
   ext_df.extraction_date ← PARSE_DATE(ext_df.extraction_date)

   ext_df ← FILTER ext_df WHERE status ≠ 'suspendu'          <span class="comment">// Supprimer suspendus</span>

3. ── <span class="kw">AGRÉGATION & ANOMALIES</span> ──────────────────────────────
   summary_df ← GROUP ext_df BY cuti:
       last_login      = MAX(last_login)      <span class="comment">// Plus récente</span>
       extraction_date = FIRST(extraction_date) <span class="comment">// Unique</span>
       lib_anomaly     = (COUNT_UNIQUE(lib) > 1)
       lputi_extracted = FIRST(lputi)
       lputi_anomaly   = (COUNT_UNIQUE(lputi) > 1)
       status_anomaly  = (COUNT_UNIQUE(status) > 1)
   <span class="kw">END GROUP</span>

4. ── <span class="kw">FUSION RH ↔ EXT</span> ─────────────────────────────────
   merged ← LEFT_MERGE(summary_df, rh_df, on=(cuti=rh_id), indicator=_merge)

   <span class="kw">FOR</span> each row IN merged <span class="kw">DO</span>
       <span class="kw">IF</span> row._merge = 'both' <span class="kw">THEN</span>
           row.category ← 'in_sgb'
       <span class="kw">ELSE</span>
           row.category ← 'out_sgb'
       <span class="kw">END IF</span>

       <span class="comment">// Calcul des jours d’inactivité</span>
       <span class="kw">IF</span> row.last_login IS NULL <span class="kw">THEN</span>
           row.days_inactive ← +∞                <span class="comment">// Jamais utilisé</span>
       <span class="kw">ELSE</span>
           row.days_inactive ← DAYS_BETWEEN(row.extraction_date, row.last_login)
       <span class="kw">END IF</span>
   <span class="kw">END FOR</span>

5. ── <span class="kw">DÉTECTION DES DOUBLONS</span> ────────────────────────────
   in_sgb_rows ← FILTER merged WHERE category='in_sgb'
   full_names  ← [r.last_name + " " + r.first_name FOR r IN in_sgb_rows]
   <span class="kw">IF ANY</span> DUPLICATE(full_names) <span class="kw">THEN</span>
       PRINT "Doublons détectés" AND EXIT(84)
   <span class="kw">END IF</span>

6. ── <span class="kw">CONSTRUCTION DU RAPPORT</span> ─────────────────────────────
   report_rows ← EMPTY LIST

   <span class="kw">FOR</span> each r IN merged <span class="kw">DO</span>
       // Initialisation des champs
       code_utilisateur = r.cuti
       nom_prenom       = ""
       profil           = ""
       direction        = ""
       recommandation   = "A certifier"
       commentaire_revue = ""
       certificateur    = certificateur
       décision         = ""
       exécution        = ""
       exécuté_par      = ""
       commentaire_exécution = ""

       <span class="kw">IF</span> r.category = 'in_sgb' <span class="kw">THEN</span>
           nom_prenom = r.last_name + " " + r.first_name
           profil     = r.position
           direction  = r.direction

           // Décision automatique
           <span class="kw">IF</span> r.days_inactive > SETTINGS.threshold_days_inactive <span class="kw">THEN</span>
               décision = "A désactiver"
           <span class="kw">ELSE</span>
               décision = "A conserver"
           <span class="kw">END IF</span>

           // Exécution priorise désactivation
           <span class="kw">IF</span> décision = "A désactiver" <span class="kw">THEN</span>
               exécution = "Désactivé"
           <span class="kw">ELSE</span>
               score = FUZZY_SCORE(profil, r.lputi_extracted)
               <span class="kw">IF</span> score < 85 <span class="kw">THEN</span>
                   exécution = "Modifié"
               <span class="kw">ELSE</span>
                   exécution = "Conservé"
               <span class="kw">END IF</span>
           <span class="kw">END IF</span>
       <span class="kw">END IF</span>

       APPEND(report_rows, (...))
   <span class="kw">END FOR</span>

   report_df ← DATAFRAME(report_rows, columns=[...])

7. ── <span class="kw">INJECTION DANS EXCEL</span> ───────────────────────────────
   wb ← LOAD_WORKBOOK(template_path)
   ws ← wb.active
   header_map ← {NORMALIZE(c.value):c.column FOR c IN ws[1]}

   <span class="kw">FOR</span> i FROM 0 TO report_df.rows-1 <span class="kw">DO</span>
       <span class="kw">FOR</span> each (col,value) IN report_df.row(i) <span class="kw">DO</span>
           hdr       = TEMPLATE_HEADER[col]
           col_index = header_map[NORMALIZE(hdr)]
           ws.cell(row=i+2,col=col_index,value=value)
       <span class="kw">END FOR</span>
   <span class="kw">END FOR</span>

   wb.save(output_path)  <span class="comment">// Fichier final</span>

8. ── <span class="kw">FLUX MAIL OUT SGB</span> (optionnel) ─────────────────────
   <span class="kw">IF</span> do_outsgb AND email_list PROVIDED <span class="kw">THEN</span>
       addresses = READ_LINES(email_list)
       outlook = INIT_OUTLOOK_COM()
       <span class="kw">FOR</span> each addr IN addresses <span class="kw">DO</span>
           mail = outlook.CreateItem()
           mail.To      = addr
           mail.Subject = "Validation comptes externes – " + certificateur
           mail.Body    = <<message standard>>

           attachment = PATH_JOIN("outsgb", addr+".xlsx")
           mail.Attachments.Add(attachment)

           <span class="kw">TRY</span>
               mail.Send()
               LOG_SEND_RESULT(addr,"Succès","")
           <span class="kw">CATCH</span> e
               LOG_SEND_RESULT(addr,"Échec",e.message)
           <span class="kw">END TRY</span>
       <span class="kw">END FOR</span>
   <span class="kw">END IF</span>

<span class="kw">END ALGORITHM</span>