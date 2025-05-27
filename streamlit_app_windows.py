import streamlit as st
import pandas as pd
from pathlib import Path
import tempfile
import os

# Import de vos modules existants
from rh_utils import charger_et_preparer_rh
from ext_utils import charger_et_preparer_ext
from match_utils import associer_rh_aux_utilisateurs
from anomalies import detecter_anomalies, extraire_cas_a_verifier
from report import inject_to_template

st.set_page_config(
    page_title="Certificateur de Comptes",
    page_icon="🔐",
    layout="wide"
)

def main():
    st.title("🔐 Certificateur de Comptes Utilisateurs")
    
    # Sidebar pour navigation
    page = st.sidebar.selectbox(
        "Navigation",
        ["📁 Upload & Configuration", "🔍 Analyse des Anomalies", "✅ Validation Manuelle", "📊 Rapport Final"]
    )
    
    # Initialisation des données en session
    if 'processed_data' not in st.session_state:
        st.session_state.processed_data = None
    if 'cas_a_verifier' not in st.session_state:
        st.session_state.cas_a_verifier = None
    
    if page == "📁 Upload & Configuration":
        upload_page()
    elif page == "🔍 Analyse des Anomalies":
        analyse_page()
    elif page == "✅ Validation Manuelle":
        validation_page()
    elif page == "📊 Rapport Final":
        rapport_page()

def upload_page():
    st.header("Configuration et Upload des Fichiers")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Fichiers RH")
        rh_files = st.file_uploader(
            "Sélectionnez les fichiers RH (Excel)",
            type=['xlsx', 'xls'],
            accept_multiple_files=True,
            key="rh_files"
        )
    
    with col2:
        st.subheader("💻 Extraction Applicative")
        ext_file = st.file_uploader(
            "Sélectionnez le fichier d'extraction",
            type=['xlsx', 'xls'],
            key="ext_file"
        )
    
    # Configuration
    st.subheader("⚙️ Configuration")
    col3, col4 = st.columns(2)
    
    with col3:
        certificateur = st.text_input("Nom du certificateur", value="")
    
    with col4:
        template_file = st.file_uploader(
            "Template de rapport (Excel)",
            type=['xlsx', 'xls'],
            key="template"
        )
    
    # Bouton de traitement
    if st.button("🚀 Lancer l'analyse", type="primary"):
        if rh_files and ext_file and certificateur:
            with st.spinner("Traitement en cours..."):
                try:
                    # Sauvegarde temporaire des fichiers
                    temp_dir = tempfile.mkdtemp()
                    
                    # Traitement RH
                    rh_paths = []
                    for rh_file in rh_files:
                        rh_path = os.path.join(temp_dir, rh_file.name)
                        with open(rh_path, 'wb') as f:
                            f.write(rh_file.read())
                        rh_paths.append(rh_path)
                    
                    # Traitement extraction
                    ext_path = os.path.join(temp_dir, ext_file.name)
                    with open(ext_path, 'wb') as f:
                        f.write(ext_file.read())
                    
                    # Traitement des données
                    rh_df = charger_et_preparer_rh(rh_paths)
                    ext_df = charger_et_preparer_ext(ext_path)
                    ext_df = associer_rh_aux_utilisateurs(ext_df, rh_df)
                    ext_df = detecter_anomalies(ext_df, certificateur=certificateur)
                    cas_a_verifier = extraire_cas_a_verifier(ext_df)
                    
                    # Stockage en session
                    st.session_state.processed_data = ext_df
                    st.session_state.cas_a_verifier = cas_a_verifier
                    st.session_state.certificateur = certificateur
                    st.session_state.template_file = template_file
                    
                    st.success("✅ Analyse terminée ! Passez à l'étape suivante.")
                    
                except Exception as e:
                    st.error(f"❌ Erreur lors du traitement : {str(e)}")
        else:
            st.warning("⚠️ Veuillez remplir tous les champs obligatoires.")

def analyse_page():
    st.header("🔍 Analyse des Anomalies Détectées")
    
    if st.session_state.processed_data is None:
        st.warning("⚠️ Veuillez d'abord uploader et traiter les fichiers.")
        return
    
    df = st.session_state.processed_data
    
    # Métriques générales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👥 Total Utilisateurs", len(df))
    
    with col2:
        anomalies_count = len(df[df['anomalie'].str.len() > 0])
        st.metric("⚠️ Anomalies Détectées", anomalies_count)
    
    with col3:
        comptes_non_rh = len(df[df['compte_non_rh'] == True])
        st.metric("❌ Comptes Non-RH", comptes_non_rh)
    
    with col4:
        cas_a_verifier = len(st.session_state.cas_a_verifier) if st.session_state.cas_a_verifier is not None else 0
        st.metric("🔍 Cas à Vérifier", cas_a_verifier)
    
    # Tableau des anomalies
    st.subheader("📋 Détail des Anomalies")
    
    # Filtres
    col1, col2 = st.columns(2)
    with col1:
        type_anomalie = st.selectbox(
            "Filtrer par type d'anomalie",
            ["Toutes"] + list(df[df['anomalie'].str.len() > 0]['anomalie'].unique())
        )
    
    with col2:
        show_only_to_verify = st.checkbox("Afficher seulement les cas à vérifier")
    
    # Application des filtres
    filtered_df = df.copy()
    
    if type_anomalie != "Toutes":
        filtered_df = filtered_df[filtered_df['anomalie'].str.contains(type_anomalie, na=False)]
    
    if show_only_to_verify:
        filtered_df = filtered_df[
            (filtered_df['anomalie'].str.len() > 0) & 
            (filtered_df['decision_manuelle'] == "")
        ]
    
    # Affichage du tableau
    if len(filtered_df) > 0:
        st.dataframe(
            filtered_df[['code_utilisateur', 'nom_prenom', 'profil', 'direction', 
                        'profil_rh', 'direction_rh', 'days_inactive', 'anomalie', 'decision_manuelle']],
            use_container_width=True
        )
    else:
        st.info("Aucune donnée ne correspond aux filtres sélectionnés.")

def validation_page():
    st.header("✅ Validation Manuelle des Cas")
    
    if st.session_state.cas_a_verifier is None:
        st.warning("⚠️ Aucun cas à vérifier ou données non chargées.")
        return
    
    cas_a_verifier = st.session_state.cas_a_verifier
    
    if len(cas_a_verifier) == 0:
        st.success("🎉 Tous les cas ont été traités !")
        return
    
    st.info(f"📝 {len(cas_a_verifier)} cas nécessitent une validation manuelle")
    
    # Interface de validation cas par cas
    for idx, (_, cas) in enumerate(cas_a_verifier.iterrows()):
        with st.expander(f"Cas {idx + 1}: {cas.get('nom_prenom', '')} ({cas.get('code_utilisateur', '')})"):
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Informations Utilisateur:**")
                st.write(f"- Code: {cas.get('code_utilisateur', '')}")
                st.write(f"- Nom: {cas.get('nom_prenom', '')}")
                st.write(f"- Jours d'inactivité: {cas.get('days_inactive', 'N/A')}")
            
            with col2:
                st.write("**Comparaison Profil/Direction:**")
                st.write(f"- Profil App: `{cas.get('profil', '')}`")
                st.write(f"- Profil RH: `{cas.get('profil_rh', '')}`")
                st.write(f"- Direction App: `{cas.get('direction', '')}`")
                st.write(f"- Direction RH: `{cas.get('direction_rh', '')}`")
            
            st.write(f"**Anomalie:** {cas.get('anomalie', '')}")
            
            # Actions possibles
            anomalie = cas.get('anomalie', '')
            if "Changement de profil à vérifier" in anomalie or "Changement de direction à vérifier" in anomalie:
                actions = ["Modifier", "Conserver", "Désactiver"]
            elif "Compte non RH" in anomalie:
                actions = ["Conserver", "Désactiver"]
            else:
                actions = ["Conserver", "Désactiver"]
            
            decision = st.selectbox(
                "Décision",
                [""] + actions,
                key=f"decision_{cas.name}"
            )
            
            if decision and st.button(f"Valider la décision", key=f"validate_{cas.name}"):
                # Mise à jour de la décision
                st.session_state.processed_data.loc[cas.name, 'decision_manuelle'] = decision
                
                # Mise à jour des whitelists si nécessaire
                if decision in ["Modifier", "Conserver"]:
                    from profils_valides import ajouter_profil_valide
                    from directions_conservees import ajouter_direction_conservee
                    
                    if "Changement de profil à vérifier" in anomalie:
                        ajouter_profil_valide(cas, certificateur=st.session_state.certificateur)
                    if "Changement de direction à vérifier" in anomalie:
                        ajouter_direction_conservee(cas, certificateur=st.session_state.certificateur)
                
                # Mise à jour des cas à vérifier
                st.session_state.cas_a_verifier = st.session_state.cas_a_verifier.drop(cas.name)
                st.success(f"✅ Décision '{decision}' enregistrée pour {cas.get('nom_prenom', '')}")
                st.rerun()

def rapport_page():
    st.header("📊 Génération du Rapport Final")
    
    if st.session_state.processed_data is None:
        st.warning("⚠️ Aucune donnée à exporter.")
        return
    
    df = st.session_state.processed_data
    
    # Résumé final
    st.subheader("📈 Résumé de la Certification")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total = len(df)
        st.metric("👥 Total Comptes", total)
    
    with col2:
        decisions = df['decision_manuelle'].value_counts()
        a_desactiver = decisions.get('Désactiver', 0)
        st.metric("❌ À Désactiver", a_desactiver)
    
    with col3:
        a_modifier = decisions.get('Modifier', 0)
        st.metric("🔄 À Modifier", a_modifier)
    
    # Tableau de synthèse
    st.subheader("📋 Synthèse des Décisions")
    synthese = df.groupby(['anomalie', 'decision_manuelle']).size().reset_index(name='count')
    st.dataframe(synthese, use_container_width=True)
    
    # Export
    st.subheader("💾 Export du Rapport")
    
    if st.button("📥 Générer le rapport Excel", type="primary"):
        if st.session_state.template_file:
            try:
                # Préparation des données finales
                from main import set_decision_columns
                df_final = df.copy()
                df_final["certificateur"] = st.session_state.certificateur
                df_final["recommendation"] = "A certifier"
                df_final = set_decision_columns(df_final)
                
                # Génération du fichier temporaire
                temp_output = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
                temp_template = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
                
                with temp_template as f:
                    f.write(st.session_state.template_file.read())
                
                inject_to_template(df_final, temp_template.name, temp_output.name, 
                                 certificateur=st.session_state.certificateur)
                
                # Téléchargement
                with open(temp_output.name, 'rb') as f:
                    st.download_button(
                        label="📥 Télécharger le rapport",
                        data=f.read(),
                        file_name=f"rapport_certification_{st.session_state.certificateur}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                
                st.success("✅ Rapport généré avec succès !")
                
            except Exception as e:
                st.error(f"❌ Erreur lors de la génération : {str(e)}")
        else:
            st.error("❌ Template de rapport manquant.")

if __name__ == "__main__":
    main()