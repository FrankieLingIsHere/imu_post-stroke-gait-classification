import unittest
from src.data.recruitment_gate import REQUIREMENTS, evaluate


class RecruitmentTests(unittest.TestCase):
    def test_primary_does_not_require_feet_or_nonstroke(self):
        r=self.valid();r['evaluation_profile']='primary_lower_back_paired'
        for k in ('bilateral_feet','nonstroke_comparison_groups','synchronized_signals'):
            r['evidence'].pop(k)
        r['participant_counts']['nonstroke']=0;r['sensor'].pop('gyroscope_unit')
        self.assertEqual(evaluate(r)['decision'],'schema_ready_for_metadata_intake')
        r['evaluation_profile']='full_comparison'
        self.assertEqual(evaluate(r)['decision'],'hold')

    def test_specificity_does_not_imply_stroke_validation(self):
        r=self.valid();r['evaluation_profile']='lower_back_nonstroke_specificity'
        r['participant_counts']['stroke']=0;r['evidence'].pop('paired_stroke_healthy_release')
        result=evaluate(r)
        self.assertEqual(result['decision'],'schema_ready_for_metadata_intake')
        self.assertIn('not stroke sensitivity',result['supported_endpoint'])
        r['participant_counts']['nonstroke']=0
        self.assertEqual(evaluate(r)['decision'],'hold')

    def test_invalid_profile_cannot_bypass_gate(self):
        for name in ('anything', [], None):
            r=self.valid();r['evaluation_profile']=name
            self.assertEqual(evaluate(r)['decision'],'hold')

    def test_raw_permission_overlap_still_required_in_every_profile(self):
        for profile in ('full_comparison','primary_lower_back_paired','lower_back_nonstroke_specificity'):
            for field in ('raw_or_lossless_signals','external_evaluation_permission','no_development_or_tuning_overlap','provider_schema_sample_reviewed'):
                r=self.valid();r['evaluation_profile']=profile;r['evidence'].pop(field)
                self.assertEqual(evaluate(r)['decision'],'hold')

    def valid(self):
        return dict(schema_version=1, provider_id='synthetic_provider', dataset_id='synthetic_new_cohort',
            reviewer='test reviewer', reviewed_on='2026-09-08', intended_role='final_external_test',
            evidence={k:dict(status='confirmed', reference='synthetic dictionary section 1') for k in REQUIREMENTS},
            sensor=dict(sampling_rate_hz=128,device_model='test device',channel_order='LB xyz, LF xyz, RF xyz',
                        axis_convention='test dictionary',walking_annotation_format='sample bounds',
                        acceleration_unit='m/s^2',gyroscope_unit='rad/s'),
            participant_counts=dict(healthy=100,stroke=100,nonstroke=100))

    def test_complete_schema_only_passes_intake(self):
        result=evaluate(self.valid())
        self.assertEqual(result['decision'],'schema_ready_for_metadata_intake')
        self.assertFalse(result['final_test_opening_authorized'])
        self.assertFalse(result['archive_download_authorized'])

    def test_each_missing_fact_blocks(self):
        for name in REQUIREMENTS:
            with self.subTest(name=name):
                r=self.valid(); del r['evidence'][name]
                self.assertEqual(evaluate(r)['decision'],'hold')

    def test_assertion_without_evidence_blocks(self):
        r=self.valid();r['evidence']['documented_lower_back']['reference']='pending'
        self.assertEqual(evaluate(r)['decision'],'hold')

    def test_known_source_blocks(self):
        r=self.valid();r['dataset_id']='voisard_2025'
        self.assertEqual(evaluate(r)['decision'],'hold')

    def test_invalid_sensor_and_population(self):
        for hz in (0, float('nan'), True, '100'):
            r=self.valid();r['sensor']['sampling_rate_hz']=hz
            self.assertEqual(evaluate(r)['decision'],'hold')
        r=self.valid();r['participant_counts']['stroke']=0
        self.assertEqual(evaluate(r)['decision'],'hold')

    def test_empty_schema_and_wrong_nested_types(self):
        self.assertEqual(evaluate({})['decision'],'hold')
        r=self.valid();r['sensor']=None;r['evidence']=[]
        self.assertEqual(evaluate(r)['decision'],'hold')
