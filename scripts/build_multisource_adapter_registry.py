from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'data'/'processed'/'multisource_adapter_registry.csv'
rows=[
 {'dataset':'marea_2017','healthy':True,'format':'MAT','observed_locations':'waist;left_foot;right_foot','canonical_lb':True,'canonical_lf':True,'canonical_rf':True,'cycle_events':True,'role':'canonical_synthesis_candidate','status':'verified'},
 {'dataset':'duogait_2023','healthy':True,'format':'CSV','observed_locations':'sacrum;left_foot;right_foot','canonical_lb':'proxy','canonical_lf':True,'canonical_rf':True,'cycle_events':True,'role':'canonical_candidate_with_trunk_proxy','status':'conditional'},
 {'dataset':'gaitmotion_2025','healthy':True,'format':'PKL','observed_locations':'paired_left_right_files;placement_to_verify','canonical_lb':'unknown','canonical_lf':'unknown','canonical_rf':'unknown','cycle_events':True,'role':'adapter_audit_required','status':'unverified'},
 {'dataset':'oxwalk_2022','healthy':True,'format':'MAT/CSV','observed_locations':'hip;wrist','canonical_lb':False,'canonical_lf':False,'canonical_rf':False,'cycle_events':'limited','role':'domain_pretraining/separate_test','status':'noncanonical'},
 {'dataset':'camargo_2021','healthy':True,'format':'MAT/CSV','observed_locations':'separate locomotion format','canonical_lb':'unknown','canonical_lf':'unknown','canonical_rf':'unknown','cycle_events':'unknown','role':'adapter_audit_required','status':'unparseable'},
]
pd.DataFrame(rows).to_csv(OUT,index=False); print(pd.DataFrame(rows).to_string(index=False)); print('wrote',OUT)
