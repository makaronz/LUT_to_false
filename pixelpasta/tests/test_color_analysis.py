import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import (
    slog3_curve,
    inverse_slog3_curve,
    rec709_oetf,
    interpolate_1d_lut,
    interpolate_3d_lut,
    s_gamut3_to_rec709,
    s_gamut3_cine_to_rec709,
    generate_table,
    logc4_curve,
    inverse_logc4_curve,
    logc_curve,
    inverse_logc_curve,
)
import tempfile
import os


class TestColorAnalysis(unittest.TestCase):
    def test_slog3_curve(self):
        # Oficjalne wartości Sony S-Log3.
        self.assertAlmostEqual(float(slog3_curve(np.array([0.18]))[0]), 0.4105571848, places=6)
        self.assertAlmostEqual(float(slog3_curve(np.array([0.0]))[0]), 0.0928641251, places=6)
        # Krzywa musi być ciągła w punkcie sklejenia 0.01125.
        below = float(slog3_curve(np.array([0.01125 - 1e-9]))[0])
        above = float(slog3_curve(np.array([0.01125 + 1e-9]))[0])
        self.assertAlmostEqual(below, above, places=5)

    def test_inverse_slog3_curve(self):
        x = np.array([0.0, 0.02, 0.18, 0.5, 1.0])
        self.assertTrue(np.allclose(inverse_slog3_curve(slog3_curve(x)), x, atol=1e-6))

    def test_logc4_curve(self):
        # Oficjalne wartości ARRI LogC4 (0-1, bez wartości > 1).
        self.assertAlmostEqual(float(logc4_curve(np.array([0.18]))[0]), 0.2783958365, places=6)
        self.assertLessEqual(float(logc4_curve(np.array([1.0]))[0]), 1.0)

    def test_inverse_logc4_curve(self):
        x = np.array([0.0, 0.02, 0.18, 0.5, 1.0])
        self.assertTrue(np.allclose(inverse_logc4_curve(logc4_curve(x)), x, atol=1e-6))

    def test_logc3_curve(self):
        # Oficjalne wartości ARRI LogC3 EI800.
        self.assertAlmostEqual(float(logc_curve(np.array([0.18]))[0]), 0.3910068320, places=6)
        x = np.array([0.0, 0.02, 0.18, 0.5, 1.0])
        self.assertTrue(np.allclose(inverse_logc_curve(logc_curve(x)), x, atol=1e-6))

    def test_rec709_oetf(self):
        self.assertAlmostEqual(float(rec709_oetf(np.array([0.0]))[0]), 0.0)
        self.assertAlmostEqual(float(rec709_oetf(np.array([0.018]))[0]), 0.08124794403514046)
        self.assertAlmostEqual(float(rec709_oetf(np.array([1.0]))[0]), 1.0)

    def test_interpolate_1d_lut(self):
        lut_1d = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        input_values = np.array([0.0, 0.5, 1.0])
        output = interpolate_1d_lut(lut_1d, input_values)
        self.assertTrue(np.allclose(output, np.array([0.0, 0.5, 1.0])))

    def test_interpolate_3d_lut(self):
        # Kolejność .cube: czerwony zmienia się najszybciej.
        lut_3d = np.array(
            [
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 1.0],
                [0.0, 1.0, 0.0],
                [0.0, 1.0, 1.0],
                [1.0, 0.0, 0.0],
                [1.0, 0.0, 1.0],
                [1.0, 1.0, 0.0],
                [1.0, 1.0, 1.0],
            ]
        )
        input_values = np.array([0.0, 0.5, 1.0])
        output = interpolate_3d_lut(lut_3d, 2, input_values)
        self.assertTrue(np.allclose(output, np.array([0.0, 0.5, 1.0])))

    def test_color_space_matrices(self):
        rgb_values = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        # Każdy wiersz macierzy konwersji D65 -> D65 sumuje się do 1.
        for fn in (s_gamut3_to_rec709, s_gamut3_cine_to_rec709):
            out = fn(rgb_values)
            # rgb=I => out = kolumny macierzy; suma po wierszach macierzy = suma po
            # kolumnach out = 1 dla każdego wiersza macierzy.
            self.assertTrue(np.allclose(out.sum(axis=0), 1.0, atol=1e-4))
        # Konkretna wartość: biel (1,1,1) mapuje się na biel Rec.709 (1,1,1).
        white = np.array([[1.0, 1.0, 1.0]])
        self.assertTrue(np.allclose(s_gamut3_to_rec709(white), 1.0, atol=1e-4))

    def test_generate_table(self):
        content = (
            'TITLE "Test LUT"\n'
            "LUT_1D_SIZE 2\n"
            "0.0 0.0 0.0\n"
            "1.0 1.0 1.0\n"
        )
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as temp_file:
            temp_file.write(content.encode())
            filepath = temp_file.name
        try:
            df = generate_table(filepath, "S-Gamut3")
            self.assertIsInstance(df, pd.DataFrame)
            self.assertEqual(len(df), 20)
            self.assertEqual(df["Color Space"][0], "S-Gamut3")
        finally:
            os.remove(filepath)


if __name__ == "__main__":
    unittest.main()
