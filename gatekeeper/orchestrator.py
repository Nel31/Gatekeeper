# gatekeeper/orchestrator.py
import logging
import pandas as pd
from .validator import validate_dataframe,validate_rh_dataframe
from .cleaner import clean_dataframe
from .aggregator import aggregate_dataframe
from .classifier import classify_accounts
from .duplicate_detector import check_duplicates
from .report_builder import build_report
from .injector import inject_to_template

logging.basicConfig(filename='gatekeeper.log',format='%(asctime)s %(levelname)s %(message)s',level=logging.INFO)

def run_pipeline(rh_path,ext_path,template_insgb,output_insgb,certificateur):
    rh_df=pd.read_excel(rh_path)
    ext_df=pd.read_excel(ext_path)
    rh_df=validate_rh_dataframe(rh_df)
    ext_df=validate_dataframe(ext_df)
    ext_df=clean_dataframe(ext_df)
    summary=aggregate_dataframe(ext_df)
    classified=classify_accounts(summary,rh_df)
    check_duplicates(classified)
    report=build_report(classified,certificateur)
    inject_to_template(report,template_insgb,output_insgb)
    logging.info(f"In SGB report at {output_insgb} by {certificateur}")
