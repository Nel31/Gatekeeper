import streamlit as st
import pandas as pd
import io
from datetime import datetime
import tempfile
import os

# Import de vos modules existants
from rh_utils import charger_et_preparer_rh
from ext_utils import charger_et_preparer_ext
from match_utils import associer_rh_aux_utilisateurs
from anomalies import detecter_anomalies, extraire_cas_a_verifier
from report import inject_to_template
from profils_valides import ajouter_profil_valide, charger_profils_valides
from directions_conservees import ajouter_direction_conservee, charger_directions_conservees

# Configuration de la page
st.set_page_config(
    page_title="Certification des Comptes Utilisateurs",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialisation du state
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'ext_df' not in st.session_state:
    st.session_state.ext_df = None
if 'cas_a_verifier' not in st.session_state:
    st.session_state.cas_a_verifier = None
if 'certificateur' not in st.session_state:
    st.session_state.certificateur = ""

def reset_workflow():
    """Remet à zéro le workflow"""
    st.session_state.step = 1
    st.session_state.ext_df = None
    st.session_state.cas_a_verifier = None
    st.session_state.certificateur = ""

def afficher_sidebar():
    """Affiche la sidebar avec navigation et informations"""
    st.sidebar.title("🔐 Certification des Comptes")
    
    # Informations sur l'étape actuelle
    steps = [
        "📁 Chargement des données",
        "🔍 Détection des anomalies", 
        "✅ Validation manuelle",
        "📊 Génération du rapport"
    ]
    
    for i, step_name in enumerate(steps, 1):
        if i == st.session_state.step:
            st.sidebar.markdown(f"**➤ {step_name}**")
        elif i < st.session_state.step:
            st.sidebar.markdown(f"✓ {step_name}")
        else:
            st.sidebar.markdown(f"⬜ {step_name}")
    
    st.sidebar.divider()
    
    # Informations sur les données chargées
    if st.session_state.ext_df is not None:
        st.sidebar.info(f"**Données chargées:**\n{len(st.session_state.ext_df)} comptes utilisateurs")
        
        if st.session_state.cas_a_verifier is not None:
            nb_cas = len(st.session_state.cas_a_verifier)
            st.sidebar.warning(f"**Cas à vérifier:** {nb_cas}")
    
    # Bouton de reset
    st.sidebar.divider()
    if st.sidebar.button("🔄 Recommencer", type="secondary"):
        reset_workflow()
        st.rerun()

def etape_chargement():
    """Étape 1: Chargement des fichiers"""
    st.header("📁 Chargement des données")
    
    # Nom du certificateur
    certificateur = st.text_input(
        "Nom du certificateur *",
        value=st.session_state.certificateur,
        help="Votre nom sera associé aux validations"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Fichiers RH")
        fichiers_rh = st.file_uploader(
            "Sélectionnez les fichiers RH (.xlsx)",
            type=['xlsx'],
            accept_multiple_files=True,
            help="Fichiers contenant les données RH de référence"
        )
        
        if fichiers_rh:
            st.success(f"{len(fichiers_rh)} fichier(s) RH sélectionné(s)")
            for f in fichiers_rh:
                st.write(f"• {f.name}")
    
    with col2:
        st.subheader("Fichier d'extraction")
        fichier_extraction = st.file_uploader(
            "Sélectionnez le fichier d'extraction (.xlsx)",
            type=['xlsx'],
            help="Fichier d'extraction de l'application à auditer"
        )
        
        if fichier_extraction:
            st.success(f"Fichier d'extraction: {fichier_extraction.name}")
    
    # Template de rapport
    st.subheader("Template de rapport")
    template_file = st.file_uploader(
        "Sélectionnez le template Excel (.xlsx)",
        type=['xlsx'],
        help="Template pour générer le rapport final"
    )
    
    if template_file:
        st.success(f"Template: {template_file.name}")
    
    # Bouton de traitement
    if certificateur and fichiers_rh and fichier_extraction and template_file:
        if st.button("🚀 Traiter les données", type="primary"):
            with st.spinner("Traitement en cours..."):
                try:
                    # Sauvegarde temporaire des fichiers
                    rh_paths = []
                    for f in fichiers_rh:
                        temp_path = f"/tmp/{f.name}"
                        with open(temp_path, "wb") as temp_file:
                            temp_file.write(f.read())
                        rh_paths.append(temp_path)
                    
                    ext_temp_path = f"/tmp/{fichier_extraction.name}"
                    with open(ext_temp_path, "wb") as temp_file:
                        temp_file.write(fichier_extraction.read())
                    
                    template_temp_path = f"/tmp/{template_file.name}"
                    with open(template_temp_path, "wb") as temp_file:
                        temp_file.write(template_file.read())
                    
                    # Traitement des données
                    rh_df = charger_et_preparer_rh(rh_paths)
                    ext_df = charger_et_preparer_ext(ext_temp_path)
                    ext_df = associer_rh_aux_utilisateurs(ext_df, rh_df)
                    ext_df = detecter_anomalies(ext_df, certificateur=certificateur)
                    cas_a_verifier = extraire_cas_a_verifier(ext_df)
                    
                    # Mise à jour du state
                    st.session_state.ext_df = ext_df
                    st.session_state.cas_a_verifier = cas_a_verifier
                    st.session_state.certificateur = certificateur
                    st.session_state.template_path = template_temp_path
                    st.session_state.step = 2
                    
                    st.success("Données traitées avec succès !")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Erreur lors du traitement: {str(e)}")
    else:
        st.info("Veuillez renseigner tous les champs pour continuer.")

def etape_detection():
    """Étape 2: Affichage des anomalies détectées"""
    st.header("🔍 Anomalies détectées")
    
    df = st.session_state.ext_df
    cas_a_verifier = st.session_state.cas_a_verifier
    
    # Statistiques générales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total comptes", len(df))
    with col2:
        nb_anomalies = len(df[df['anomalie'].str.len() > 0])
        st.metric("Comptes avec anomalies", nb_anomalies)
    with col3:
        st.metric("Cas à vérifier manuellement", len(cas_a_verifier))
    with col4:
        nb_auto = len(df[df['decision_manuelle'] != ""])
        st.metric("Décisions automatiques", nb_auto)
    
    # Répartition des anomalies
    st.subheader("Répartition des anomalies")
    
    anomalies_count = {}
    for anomalie in df['anomalie']:
        if anomalie:
            for a in anomalie.split(', '):
                anomalies_count[a] = anomalies_count.get(a, 0) + 1
    
    if anomalies_count:
        anomalies_df = pd.DataFrame(list(anomalies_count.items()), 
                                  columns=['Type d\'anomalie', 'Nombre'])
        st.bar_chart(anomalies_df.set_index('Type d\'anomalie'))
    
    # Affichage des cas avec décisions automatiques
    cas_auto = df[(df['decision_manuelle'] != "") & (~df.index.isin(cas_a_verifier.index))]
    if len(cas_auto) > 0:
        st.subheader(f"🤖 Cas traités automatiquement ({len(cas_auto)})")
        
        # Colonnes à afficher
        cols_display = ['code_utilisateur', 'nom_prenom', 'anomalie', 'decision_manuelle']
        st.dataframe(
            cas_auto[cols_display],
            use_container_width=True,
            hide_index=True
        )
    
    # Affichage des cas à vérifier
    if len(cas_a_verifier) > 0:
        st.subheader(f"⚠️ Cas nécessitant une validation manuelle ({len(cas_a_verifier)})")
        
        # Aperçu des cas à vérifier
        cols_display = ['code_utilisateur', 'nom_prenom', 'profil', 'profil_rh', 
                       'direction', 'direction_rh', 'days_inactive', 'anomalie']
        st.dataframe(
            cas_a_verifier[cols_display],
            use_container_width=True,
            hide_index=True
        )
        
        if st.button("➡️ Passer à la validation manuelle", type="primary"):
            st.session_state.step = 3
            st.rerun()
    else:
        st.success("✅ Aucun cas nécessitant une validation manuelle !")
        if st.button("➡️ Générer le rapport", type="primary"):
            st.session_state.step = 4
            st.rerun()

def etape_validation():
    """Étape 3: Validation manuelle des cas"""
    st.header("✅ Validation manuelle")
    
    cas_a_verifier = st.session_state.cas_a_verifier
    
    if len(cas_a_verifier) == 0:
        st.success("Tous les cas ont été traités !")
        if st.button("➡️ Générer le rapport", type="primary"):
            st.session_state.step = 4
            st.rerun()
        return
    
    st.info(f"Il reste {len(cas_a_verifier)} cas à valider")
    
    # Sélection du cas à traiter
    if len(cas_a_verifier) > 1:
        cas_options = []
        for idx, row in cas_a_verifier.iterrows():
            cas_options.append(f"{row['code_utilisateur']} - {row.get('nom_prenom', 'N/A')}")
        
        cas_selectionne_idx = st.selectbox(
            "Sélectionnez le cas à traiter:",
            range(len(cas_options)),
            format_func=lambda x: cas_options[x]
        )
        cas_idx = cas_a_verifier.index[cas_selectionne_idx]
        cas = cas_a_verifier.loc[cas_idx]
    else:
        cas_idx = cas_a_verifier.index[0]
        cas = cas_a_verifier.loc[cas_idx]
    
    # Affichage détaillé du cas
    st.subheader("📋 Détails du cas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Informations utilisateur:**")
        st.write(f"• Code utilisateur: `{cas.get('code_utilisateur', 'N/A')}`")
        st.write(f"• Nom/Prénom: `{cas.get('nom_prenom', 'N/A')}`")
        
        jours = cas.get('days_inactive', '')
        jours_affiche = f"{jours:.0f}" if isinstance(jours, (int, float)) and not pd.isna(jours) else "Non renseigné"
        st.write(f"• Jours d'inactivité: `{jours_affiche}`")
    
    with col2:
        st.write("**Comparaison Extraction vs RH:**")
        st.write(f"• Profil extraction: `{cas.get('profil', 'N/A')}`")
        st.write(f"• Profil RH: `{cas.get('profil_rh', 'N/A')}`")
        st.write(f"• Direction extraction: `{cas.get('direction', 'N/A')}`")
        st.write(f"• Direction RH: `{cas.get('direction_rh', 'N/A')}`")
    
    # Anomalie détectée
    st.warning(f"**Anomalie détectée:** {cas.get('anomalie', 'N/A')}")
    
    # Actions possibles
    st.subheader("🎯 Actions possibles")
    
    anomalie = cas.get('anomalie', '')
    
    # Définition des actions selon l'anomalie
    if "Changement de profil à vérifier" in anomalie or "Changement de direction à vérifier" in anomalie:
        actions = {
            "Modifier": "Mettre à jour le profil ou la direction selon le RH (sera synchronisé dans l'application)",
            "Conserver": "Tolérer l'écart (garder la valeur actuelle dans l'application et whitelister l'écart pour le futur)",
            "Désactiver": "Désactiver ou supprimer le compte utilisateur concerné (plus d'accès possible)"
        }
    elif "Compte non RH" in anomalie:
        actions = {
            "Conserver": "Tolérer l'écart (garder la valeur actuelle dans l'application)",
            "Désactiver": "Désactiver ou supprimer le compte utilisateur concerné (plus d'accès possible)"
        }
    else:
        actions = {
            "Conserver": "Conserver le compte en l'état",
            "Désactiver": "Désactiver ou supprimer le compte utilisateur concerné (plus d'accès possible)"
        }
    
    # Sélection de l'action
    decision = st.radio(
        "Choisissez une action:",
        list(actions.keys()),
        format_func=lambda x: f"**{x}** - {actions[x]}"
    )
    
    # Commentaire optionnel
    commentaire = st.text_area(
        "Commentaire (optionnel):",
        help="Ajoutez un commentaire pour justifier votre décision"
    )
    
    # Validation
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("✅ Valider cette décision", type="primary"):
            # Mise à jour de la décision
            st.session_state.ext_df.loc[cas_idx, 'decision_manuelle'] = decision
            
            if commentaire:
                st.session_state.ext_df.loc[cas_idx, 'comment_certificateur'] = commentaire
            
            # Ajout aux whitelists si nécessaire
            if decision in ["Modifier", "Conserver"]:
                if "Changement de profil à vérifier" in anomalie:
                    ajouter_profil_valide(cas, certificateur=st.session_state.certificateur)
                if "Changement de direction à vérifier" in anomalie:
                    ajouter_direction_conservee(cas, certificateur=st.session_state.certificateur)
            
            # Mise à jour des cas à vérifier
            st.session_state.cas_a_verifier = extraire_cas_a_verifier(st.session_state.ext_df)
            
            st.success(f"Décision '{decision}' enregistrée pour {cas.get('code_utilisateur', 'N/A')}")
            st.rerun()
    
    with col2:
        if st.button("⏭️ Passer ce cas", type="secondary"):
            # Marquer comme à revoir plus tard ou passer
            st.info("Cas passé, vous pourrez y revenir plus tard")
    
    # Progression
    total_initial = len(st.session_state.ext_df[st.session_state.ext_df['anomalie'].str.len() > 0])
    reste = len(st.session_state.cas_a_verifier)
    traites = total_initial - reste
    
    progress = traites / total_initial if total_initial > 0 else 1
    st.progress(progress, text=f"Progression: {traites}/{total_initial} cas traités")

def etape_rapport():
    """Étape 4: Génération du rapport"""
    st.header("📊 Génération du rapport")
    
    df = st.session_state.ext_df
    
    # Statistiques finales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total comptes", len(df))
    with col2:
        nb_conserver = len(df[df['decision_manuelle'] == 'Conserver'])
        st.metric("À conserver", nb_conserver)
    with col3:
        nb_modifier = len(df[df['decision_manuelle'] == 'Modifier'])
        st.metric("À modifier", nb_modifier)
    with col4:
        nb_desactiver = len(df[df['decision_manuelle'] == 'Désactiver'])
        st.metric("À désactiver", nb_desactiver)
    
    # Vérification des cas non traités
    cas_non_traites = len(st.session_state.cas_a_verifier)
    if cas_non_traites > 0:
        st.warning(f"⚠️ Il reste {cas_non_traites} cas non traités. Voulez-vous continuer ?")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Retour à la validation", type="secondary"):
                st.session_state.step = 3
                st.rerun()
        with col2:
            forcer_generation = st.button("Générer le rapport malgré tout", type="primary")
    else:
        st.success("✅ Tous les cas ont été traités !")
        forcer_generation = True
    
    if forcer_generation or cas_non_traites == 0:
        # Préparation des données pour le rapport
        from main import set_decision_columns
        
        df_rapport = df.copy()
        df_rapport["certificateur"] = st.session_state.certificateur
        df_rapport["recommendation"] = "A certifier"
        df_rapport = set_decision_columns(df_rapport)
        df_rapport['date_certification'] = datetime.now().strftime('%Y-%m-%d')
        
        # Aperçu du rapport
        st.subheader("📋 Aperçu du rapport")
        
        cols_rapport = ['code_utilisateur', 'nom_prenom', 'profil', 'direction', 
                       'recommendation', 'decision', 'execution_reco_decision', 'anomalie']
        
        st.dataframe(
            df_rapport[cols_rapport],
            use_container_width=True,
            hide_index=True
        )
        
        # Génération du fichier Excel
        if st.button("📥 Télécharger le rapport Excel", type="primary"):
            try:
                # Utilisation du template sauvegardé
                output_path = f"/tmp/rapport_certification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                inject_to_template(df_rapport, st.session_state.template_path, output_path, 
                                 certificateur=st.session_state.certificateur)
                
                # Lecture du fichier généré
                with open(output_path, "rb") as file:
                    st.download_button(
                        label="📥 Télécharger le rapport",
                        data=file.read(),
                        file_name=f"rapport_certification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        type="primary"
                    )
                
                st.success("✅ Rapport généré avec succès !")
                
            except Exception as e:
                st.error(f"Erreur lors de la génération du rapport: {str(e)}")
        
        # Statistiques des whitelists
        st.subheader("📋 Historique des validations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Profils validés:**")
            try:
                profils_valides = charger_profils_valides()
                if len(profils_valides) > 0:
                    st.dataframe(profils_valides, use_container_width=True, hide_index=True)
                else:
                    st.info("Aucun profil validé")
            except:
                st.info("Aucun profil validé")
        
        with col2:
            st.write("**Directions conservées:**")
            try:
                directions_conservees = charger_directions_conservees()
                if len(directions_conservees) > 0:
                    st.dataframe(directions_conservees, use_container_width=True, hide_index=True)
                else:
                    st.info("Aucune direction conservée")
            except:
                st.info("Aucune direction conservée")

def main():
    """Application principale"""
    afficher_sidebar()
    
    # Navigation entre les étapes
    if st.session_state.step == 1:
        etape_chargement()
    elif st.session_state.step == 2:
        etape_detection()
    elif st.session_state.step == 3:
        etape_validation()
    elif st.session_state.step == 4:
        etape_rapport()

if __name__ == "__main__":
    main()