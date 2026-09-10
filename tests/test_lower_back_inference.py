"""Synthetic contract tests. These do not claim clinical or OOF reproduction."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np
import torch

from models.lower_back_ensemble import LowerBackDomainNet
from models.predict_lower_back import EXPECTED_MEMBERS, RELEASE_ID, load_bundle, predict_windows, validate_bundle


class EnsembleTests(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(1)
        model = LowerBackDomainNet()
        for parameter in model.parameters():
            parameter.data.zero_()
        self.bundle = {
            "release_id": RELEASE_ID, "format_version": 1,
            "architecture": "LowerBackDomainNet",
            "input_contract": {"shape": ["windows", 500, 1], "sampling_hz": 100,
                               "duration_seconds": 5,
                               "channel": "lower_back_acceleration_magnitude_g"},
            "members": [{"method": method, "seed": seed,
                         "mean": torch.tensor([1.]), "std": torch.tensor([.1]),
                         "model_state_dict": copy.deepcopy(model.state_dict())}
                        for method, seed in sorted(EXPECTED_MEMBERS)]}

    def test_known_probability_and_batch_invariance(self):
        x = np.ones((3, 500, 1), dtype=np.float32)
        np.testing.assert_allclose(predict_windows(self.bundle, x, 1), .5)
        np.testing.assert_allclose(predict_windows(self.bundle, x, 3), .5)

    def test_duplicate_member_rejected(self):
        self.bundle["members"][-1] = self.bundle["members"][0]
        with self.assertRaises(ValueError):
            validate_bundle(self.bundle)

    def test_probability_average_not_logit_average(self):
        logits = np.arange(15, dtype=np.float32) / 4
        for member, logit in zip(self.bundle["members"], logits):
            member["model_state_dict"]["classifier.2.bias"].fill_(float(logit))
        expected = np.mean(1 / (1 + np.exp(-logits)))
        np.testing.assert_allclose(predict_windows(self.bundle, np.ones((1, 500, 1))),
                                   expected, atol=1e-7, rtol=0)

    def test_checksum_roundtrip_and_tamper_rejection(self):
        with tempfile.TemporaryDirectory() as directory:
            checkpoint = Path(directory) / "test.pt"
            manifest = Path(directory) / "test.json"
            torch.save(self.bundle, checkpoint)
            manifest.write_text(json.dumps({"release_id": RELEASE_ID,
                "checkpoint_sha256": hashlib.sha256(checkpoint.read_bytes()).hexdigest()}))
            self.assertEqual(len(load_bundle(checkpoint, manifest)["members"]), 15)
            with checkpoint.open("ab") as handle:
                handle.write(b"tampered")
            with self.assertRaisesRegex(ValueError, "checksum"):
                load_bundle(checkpoint, manifest)

    def test_invalid_normalization_rejected(self):
        self.bundle["members"][0]["std"] = torch.tensor([float("nan")])
        with self.assertRaises(ValueError):
            validate_bundle(self.bundle)

    def test_invalid_inputs_rejected(self):
        for x in (np.ones((2, 500, 3)), np.ones((0, 500, 1)),
                  np.full((1, 500, 1), np.nan)):
            with self.assertRaises(ValueError):
                predict_windows(self.bundle, x)


if __name__ == "__main__":
    unittest.main()
