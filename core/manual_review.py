from mapping.profils_valides import ajouter_profil_valide
from mapping.directions_conservees import ajouter_direction_conservee
import pandas as pd
from colorama import Fore, Style, init

init(autoreset=True)  # Pour que la coloration se reset à chaque print

def proposer_actions(anomalie):
    # Les commentaires associés à chaque choix
    ACTION_EXPLAIN = {
        "Modifier":   "Mettre à jour le profil ou la direction selon le RH (sera synchronisé dans l'application)",
        "Conserver":  "Tolérer l'écart (garder la valeur actuelle dans l'application et whitelister l'écart pour le futur)",
        "Désactiver": "Désactiver ou supprimer le compte utilisateur concerné (plus d'accès possible)"
    }

    if "Changement de profil à vérifier" in anomalie or "Changement de direction à vérifier" in anomalie:
        actions = {
            "m": ("Modifier",   ACTION_EXPLAIN["Modifier"]),
            "d": ("Désactiver", ACTION_EXPLAIN["Désactiver"]),
            "c": ("Conserver",  ACTION_EXPLAIN["Conserver"]),
        }
    elif "Compte non RH" in anomalie:
        actions = {
            "d": ("Désactiver", ACTION_EXPLAIN["Désactiver"]),
            "c": ("Conserver",  ACTION_EXPLAIN["Conserver"]),
        }
    else:
        actions = {
            "d": ("Désactiver", ACTION_EXPLAIN["Désactiver"]),
            "c": ("Conserver",  ACTION_EXPLAIN["Conserver"]),
        }
    return actions

def afficher_resume_cas(cas, decision):
    jours = cas.get('days_inactive', '')
    jours_affiche = f"{jours:.0f}" if isinstance(jours, (int, float)) and not pd.isna(jours) else "non renseigné"
    print()
    print(f"{Fore.CYAN}{Style.BRIGHT}{'═'*45}")
    titre = 'Cas traité automatiquement' if decision else 'Cas à vérifier'
    print(f"{' ' * 12}{Fore.CYAN}{Style.BRIGHT}--- {titre} ---{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'═'*45}{Style.RESET_ALL}")
    print(f"{Fore.BLUE}Utilisateur:{Style.RESET_ALL} {cas.get('code_utilisateur', '')}")
    print(f"{Fore.BLUE}Nom/prénom:{Style.RESET_ALL} {cas.get('nom_prenom', '')}")
    print(f"{Fore.MAGENTA}Profil extraction:{Style.RESET_ALL} {cas.get('profil', '')} {Fore.LIGHTBLACK_EX}| RH:{Style.RESET_ALL} {cas.get('profil_rh', '')}")
    print(f"{Fore.MAGENTA}Direction extraction:{Style.RESET_ALL} {cas.get('direction', '')} {Fore.LIGHTBLACK_EX}| RH:{Style.RESET_ALL} {cas.get('direction_rh', '')}")
    print(f"{Fore.BLUE}Jours inactivité:{Style.RESET_ALL} {jours_affiche}")
    print(f"{Fore.YELLOW}Anomalie:{Style.RESET_ALL} {cas.get('anomalie', '')}")
    if decision:
        print(f"{Fore.GREEN}Décision automatique :{Style.RESET_ALL} {decision}")
    print(f"{Fore.CYAN}{'═'*45}{Style.RESET_ALL}")

def traiter_cas_manuels(ext_df, cas_a_verifier, certificateur=""):
    auto_cas = ext_df[(ext_df['decision_manuelle'] != "") & (~ext_df.index.isin(cas_a_verifier.index))]
    for idx, cas in auto_cas.iterrows():
        afficher_resume_cas(cas, cas['decision_manuelle'])

    for idx, cas in cas_a_verifier.iterrows():
        afficher_resume_cas(cas, None)
        actions = proposer_actions(cas.get('anomalie', ''))
        print(f"{Fore.LIGHTWHITE_EX}{Style.BRIGHT}Actions possibles :{Style.RESET_ALL}")
        for k, (libelle, commentaire) in actions.items():
            print(f"{Fore.LIGHTGREEN_EX}[{k.upper()}] {libelle}{Style.RESET_ALL} : {Fore.LIGHTBLACK_EX}{commentaire}{Style.RESET_ALL}")
        choix = ""
        while choix not in actions:
            choix = input(f"{Fore.CYAN}Décision : {Style.RESET_ALL}").strip().lower()
        decision = actions[choix][0]
        if decision in ["Modifier", "Conserver"]:
            if "Changement de profil à vérifier" in cas.get('anomalie', ''):
                ajouter_profil_valide(cas, certificateur=certificateur)
            if "Changement de direction à vérifier" in cas.get('anomalie', ''):
                ajouter_direction_conservee(cas, certificateur=certificateur)
        ext_df.loc[idx, 'decision_manuelle'] = decision
    return ext_df