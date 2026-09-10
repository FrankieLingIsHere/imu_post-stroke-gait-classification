"""Fail-closed provider schema screening; never authorizes final-test opening."""
import math

REQUIREMENTS = (
    'paired_stroke_healthy_release', 'clinical_reference_labels',
    'raw_or_lossless_signals', 'documented_lower_back', 'bilateral_feet',
    'synchronized_signals', 'controlled_or_annotated_walking',
    'matched_group_protocol', 'participant_age_sex', 'clinical_metadata_dictionary',
    'participant_trial_identifiers', 'no_development_or_tuning_overlap',
    'external_evaluation_permission', 'provider_schema_sample_reviewed',
    'sample_size_precision_plan', 'nonstroke_comparison_groups',
)
KNOWN_SOURCES = {'felius_2024', 'voisard_2025', 'sint_maartenskliniek', 'revalexo', 'nonan'}
PROFILES = {
    'full_comparison': {'omit': set(), 'groups': ('healthy', 'stroke', 'nonstroke')},
    'primary_lower_back_paired': {'omit': {'bilateral_feet', 'nonstroke_comparison_groups', 'synchronized_signals'},
                                'groups': ('healthy', 'stroke')},
    'lower_back_nonstroke_specificity': {'omit': {'bilateral_feet', 'paired_stroke_healthy_release', 'synchronized_signals'},
                                       'groups': ('healthy', 'nonstroke')},
}


def evaluate(record):
    """Confirmed assertions need traceable evidence; unknown never counts as yes."""
    blockers = []
    def require(condition, field, reason):
        if not condition:
            blockers.append({'field': field, 'reason': reason})
    def filled(value):
        return isinstance(value, str) and value.strip().lower() not in {'', 'unknown', 'pending', 'tbd'}
    require(record.get('schema_version') == 1, 'schema_version', 'Expected version 1')
    profile_name = record.get('evaluation_profile', 'full_comparison')
    valid_profile = isinstance(profile_name, str) and profile_name in PROFILES
    require(valid_profile, 'evaluation_profile', 'Unknown evaluation profile')
    profile = PROFILES[profile_name] if valid_profile else PROFILES['full_comparison']
    require(filled(record.get('provider_id')), 'provider_id', 'Provider identifier required')
    require(filled(record.get('reviewer')), 'reviewer', 'Named schema reviewer required')
    require(filled(record.get('reviewed_on')), 'reviewed_on', 'Review date required')
    require(record.get('intended_role') == 'final_external_test', 'intended_role', 'Gate is for final-test candidates')
    require(str(record.get('dataset_id', '')).strip().lower() not in KNOWN_SOURCES and filled(record.get('dataset_id')),
            'dataset_id', 'Use a new cohort identifier, not an existing development/inspected source')
    facts = record.get('evidence', {})
    if not isinstance(facts, dict):
        facts = {}
    for name in REQUIREMENTS:
        if name in profile['omit']:
            continue
        fact = facts.get(name, {})
        if not isinstance(fact, dict):
            fact = {}
        require(fact.get('status') == 'confirmed' and filled(fact.get('reference')),
                name, 'Requires confirmed provider evidence and a traceable reference')
    sensor = record.get('sensor', {})
    if not isinstance(sensor, dict):
        sensor = {}
    hz = sensor.get('sampling_rate_hz')
    require(type(hz) in (int, float) and math.isfinite(hz) and hz > 0,
            'sensor.sampling_rate_hz', 'Finite positive native sampling rate required')
    for name in ('device_model', 'channel_order', 'axis_convention', 'walking_annotation_format'):
        require(filled(sensor.get(name)), 'sensor.'+name, 'Document the native export contract')
    require(sensor.get('acceleration_unit') in ('g', 'm/s^2'), 'sensor.acceleration_unit', 'Supported explicit units: g or m/s^2')
    if profile_name == 'full_comparison':
        require(sensor.get('gyroscope_unit') in ('deg/s', 'rad/s'), 'sensor.gyroscope_unit', 'Supported explicit units: deg/s or rad/s')
    counts = record.get('participant_counts', {})
    if not isinstance(counts, dict):
        counts = {}
    for group in profile['groups']:
        require(type(counts.get(group)) is int and counts[group] > 0,
                'participant_counts.'+group, 'Positive clinically identified participant count required')
    return {
        'dataset_id': record.get('dataset_id'),
        'evaluation_profile': profile_name,
        'not_required_for_profile': sorted(profile['omit']),
        'supported_endpoint': {'primary_lower_back_paired': 'healthy versus stroke only; not non-stroke differential specificity',
                               'lower_back_nonstroke_specificity': 'healthy and non-stroke positive-call rates only; not stroke sensitivity',
                               'full_comparison': 'paired binary, non-stroke specificity, and three-sensor comparator'}.get(profile_name if valid_profile else '', 'invalid'),
        'decision': 'schema_ready_for_metadata_intake' if not blockers else 'hold',
        'blockers': blockers,
        'archive_download_authorized': False,
        'final_test_opening_authorized': False,
        'next_step': ('Validate archive metadata/schema before signal extraction; complete independent overlap and evaluation-lock checks'
                      if not blockers else 'Obtain missing provider evidence; do not acquire an archive'),
    }
