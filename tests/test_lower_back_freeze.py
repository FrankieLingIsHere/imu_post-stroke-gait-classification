"""Freeze-specific split and architecture checks without participant recordings."""
import unittest
import numpy as np
import pandas as pd
import torch

from models.lower_back_ensemble import LowerBackDomainNet
from src.models.evidence_gated_domain_generalization import BenchmarkConfig, DomainNet
from src.models.freeze_lower_back_ensemble import FreezeConfig, benchmark_config, full_development_split


class FreezeTests(unittest.TestCase):
    def test_recipe_matches_selected_benchmark(self):
        self.assertEqual(benchmark_config(FreezeConfig()), BenchmarkConfig())

    def test_split_keeps_repeated_windows_together(self):
        meta = pd.DataFrame([{"source": source, "y": label, "group": f"{source}:{label}:{person}"}
            for source in ("a", "b", "c") for label in (0, 1)
            for person in range(10) for window in range(3)])
        fit, valid = full_development_split(meta, 20260903, .2)
        self.assertFalse(set(meta.loc[fit, "group"]) & set(meta.loc[valid, "group"]))
        self.assertEqual(meta.loc[valid, "group"].nunique(), 12)
        np.testing.assert_array_equal(valid, full_development_split(meta, 20260903, .2)[1])

    def test_packaged_architecture_matches_training(self):
        torch.set_num_threads(1)
        torch.manual_seed(42)
        training = DomainNet(1).eval()
        packaged = LowerBackDomainNet().eval()
        packaged.load_state_dict(training.state_dict(), strict=True)
        x = torch.randn(3, 1, 500)
        with torch.inference_mode():
            torch.testing.assert_close(training(x), packaged(x), atol=0, rtol=0)


if __name__ == "__main__":
    unittest.main()
