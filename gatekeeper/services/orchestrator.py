import sys
from gatekeeper.adapters.excel_reader import read_excel
from gatekeeper.adapters.excel_writer import write_excel
from gatekeeper.domain.validator import validate_and_normalize
from gatekeeper.domain.cleaner import clean_dataframe
from gatekeeper.domain.aggregator import aggregate_and_detect
from gatekeeper.domain.classifier import classify_accounts
from gatekeeper.domain.duplicates import detect_duplicates
from gatekeeper.domain.report_builder import build_report

def run_pipeline(rh_path, ext_path, tpl_path, out_path):
    df_rh   = read_excel(rh_path)
    df_ext  = read_excel(ext_path)
    df_tpl  = read_excel(tpl_path)

    df_rh = validate_and_normalize(df_rh)
    df_ext = validate_and_normalize(df_ext)

    df_ext_clean = clean_dataframe(df_ext)
    df_agg, anomalies = aggregate_and_detect(df_ext_clean)
    in_sgb, out_sgb = classify_accounts(df_agg, df_rh)

    duplicates = detect_duplicates(in_sgb)
    if duplicates:
        print("Doublons détectés : ", duplicates)
        sys.exit(84)

    report_df = build_report(in_sgb, df_rh)
    write_excel(out_path, report_df, tpl_path)

    print("Pipeline exécuté avec succès.")
