import numpy as np
from src.features.sampling_audit import audit_segment


def test_low_frequency_survives_and_high_frequency_is_not_invented():
    t=np.arange(2000)/100
    low=np.column_stack([1+.1*np.sin(2*np.pi*2*t),.1*np.cos(2*np.pi*2*t),np.zeros(len(t))])
    result=audit_segment(low,100,25)
    assert result['band8_nrmse']<.04
    assert result['peak_match_f1']>.98
    noisy=low.copy();noisy[:,2]=np.sin(2*np.pi*20*t)
    assert audit_segment(noisy,100,25)['energy_above_target_nyquist']>.5
