import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])))

    def test_inverse_slog3_curve(self):
        a = 0.432699
        b = 0.009468
        c = 0.655
        d = 0.037584
        e = 0.01
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), 0.1))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), 1.0))
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), np.array([0.1])))
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), np.array([0.1])))
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), 0.1))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), 1.0))
        self.assertTrue(np.allclose(inverse_slog3_curve(np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])), np.array([ (0.01 - e) / d, 0.1, 1.0])))

    def test_rec709_oetf(self):
        self.assertAlmostEqual(rec709_oetf(0.0), 0.0)
        self.assertAlmostEqual(rec709_oetf(0.018), 0.08124794403514046)
        self.assertAlmostEqual(rec709_oetf(1.0), 1.0)
        self.assertTrue(np.allclose(rec709_oetf(np.array([0.0, 0.018, 1.0])), np.array([0.0, 0.08124794403514046, 1.0])))

    def test_interpolate_1d_lut(self):
        lut_1d = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]])
        output = interpolate_1d_lut(lut_1d, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_interpolate_3d_lut(self):
        lut_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]
        ])
        lut_size = 2
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([
            [0.  , 0.  , 0.  ],
            [0.5 , 0.5 , 0.5 ],
            [1.  , 1.  , 1.  ]
        ])
        output = interpolate_3d_lut(lut_3d, lut_size, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_srgb_to_rec709(self):
        rgb_values = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        expected_output_sgamut3 = np.array([
            [ 1.641 , -0.6636,  0.0117],
            [-0.3245,  1.6157, -0.0085],
            [-0.3165,  0.0479,  0.9968]
        ])
        expected_output_sgamut3_cine = np.array([
            [ 1.5529, -0.5428, -0.0026],
            [-0.2555,  1.5027, -0.0186],
            [-0.2974,  0.0401,  1.0212]
        ])
        output_sgamut3 = srgb_to_rec709(rgb_values, 'S-Gamut3')
        output_sgamut3_cine = srgb_to_rec709(rgb_values, 'S-Gamut3.Cine')
        self.assertTrue(np.allclose(output_sgamut3, expected_output_sgamut3))
        self.assertTrue(np.allclose(output_sgamut3_cine, expected_output_sgamut3_cine))
        with self.assertRaises(ValueError):
            srgb_to_rec709(rgb_values, 'InvalidColorSpace')

    def test_generate_table(self):
        # Tworzymy tymczasowy plik .cube
        content = """
TITLE "Test LUT"
LUT_1D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as temp_file:
            temp_file.write(content.encode())
            filepath = temp_file.name

        # Testujemy dla S-Gamut3
        df_sgamut3 = generate_table(filepath, 'S-Gamut3')
        self.assertIsInstance(df_sgamut3, pd.DataFrame)
        self.assertEqual(len(df_sgamut3), 20)
        self.assertEqual(df_sgamut3['Color Space'][0], 'S-Gamut3')

        # Testujemy dla S-Gamut3.Cine
        df_sgamut3_cine = generate_table(filepath, 'S-Gamut3.Cine')
        self.assertIsInstance(df_sgamut3_cine, pd.DataFrame)
        self.assertEqual(len(df_sgamut3_cine), 20)
        self.assertEqual(df_sgamut3_cine['Color Space'][0], 'S-Gamut3.Cine')

        os.remove(filepath) # Usuwamy tymczasowy plik

    def test_logc4_curve(self):
      self.assertTrue(np.allclose(logc4_curve(0.0), np.array([-3852.359026659536])))
      self.assertAlmostEqual(logc4_curve(0.18), 0.4090068696819821)
      self.assertTrue(np.allclose(logc4_curve(np.array([0.0, 0.18, 1.0])), np.array([-3852.359026659536, 0.4090068696819821, 0.6577136499999999])))

    def test_inverse_logc4_curve(self):
      self.assertTrue(np.allclose(inverse_logc4_curve(0.09285527796717754), np.array([0.04345044])))
      self.assertTrue(np.allclose(inverse_logc4_curve(0.4090068696819821), np.array([0.18])))
      self.assertTrue(np.allclose(inverse_logc4_curve(np.array([0.09285527796717754, 0.4090068696819821, 0.6577136499999999])), np.array([0.04345044, 0.18, 1.0])))


if __name__ == '__main__':
    unittest.main()
</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.<environment_details>
# VSCode Visible Files
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
pixelpasta/tests/test_color_analysis.py

# VSCode Open Tabs
pixelpasta/tests/test_cube_parser.py
pixelpasta/lut_processor/cube_parser.py
pixelpasta/app.py
pixelpasta/lut_processor/color_analysis.py
pixelpasta/templates/upload.html
pixelpasta/tests/test_color_analysis.py

# Current Time
19/03/2025, 6:47:05 pm (Europe/Warsaw, UTC+1:00)

# Current Mode
ACT MODE
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])))

    def test_inverse_slog3_curve(self):
        a = 0.432699
        b = 0.009468
        c = 0.655
        d = 0.037584
        e = 0.01
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), np.array([0.1])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), np.array([1.0])))
        self.assertTrue(np.allclose(inverse_slog3_curve(np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])), np.array([ (0.01 - e) / d, 0.1, 1.0])))

    def test_rec709_oetf(self):
        self.assertAlmostEqual(rec709_oetf(0.0), 0.0)
        self.assertAlmostEqual(rec709_oetf(0.018), 0.08124794403514046)
        self.assertAlmostEqual(rec709_oetf(1.0), 1.0)
        self.assertTrue(np.allclose(rec709_oetf(np.array([0.0, 0.018, 1.0])), np.array([0.0, 0.08124794403514046, 1.0])))

    def test_interpolate_1d_lut(self):
        lut_1d = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]])
        output = interpolate_1d_lut(lut_1d, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_interpolate_3d_lut(self):
        lut_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]
        ])
        lut_size = 2
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([
            [0.  , 0.  , 0.  ],
            [0.5 , 0.5 , 0.5 ],
            [1.  , 1.  , 1.  ]
        ])
        output = interpolate_3d_lut(lut_3d, lut_size, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_srgb_to_rec709(self):
        rgb_values = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        expected_output_sgamut3 = np.array([
            [ 1.641 , -0.6636,  0.0117],
            [-0.3245,  1.6157, -0.0085],
            [-0.3165,  0.0479,  0.9968]
        ])
        expected_output_sgamut3_cine = np.array([
            [ 1.5529, -0.5428, -0.0026],
            [-0.2555,  1.5027, -0.0186],
            [-0.2974,  0.0401,  1.0212]
        ])
        output_sgamut3 = srgb_to_rec709(rgb_values, 'S-Gamut3')
        output_sgamut3_cine = srgb_to_rec709(rgb_values, 'S-Gamut3.Cine')
        self.assertTrue(np.allclose(output_sgamut3, expected_output_sgamut3))
        self.assertTrue(np.allclose(output_sgamut3_cine, expected_output_sgamut3_cine))
        with self.assertRaises(ValueError):
            srgb_to_rec709(rgb_values, 'InvalidColorSpace')

    def test_generate_table(self):
        # Tworzymy tymczasowy plik .cube
        content = """
TITLE "Test LUT"
LUT_1D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as temp_file:
            temp_file.write(content.encode())
            filepath = temp_file.name

        # Testujemy dla S-Gamut3
        df_sgamut3 = generate_table(filepath, 'S-Gamut3')
        self.assertIsInstance(df_sgamut3, pd.DataFrame)
        self.assertEqual(len(df_sgamut3), 20)
        self.assertEqual(df_sgamut3['Color Space'][0], 'S-Gamut3')

        # Testujemy dla S-Gamut3.Cine
        df_sgamut3_cine = generate_table(filepath, 'S-Gamut3.Cine')
        self.assertIsInstance(df_sgamut3_cine, pd.DataFrame)
        self.assertEqual(len(df_sgamut3_cine), 20)
        self.assertEqual(df_sgamut3_cine['Color Space'][0], 'S-Gamut3.Cine')

        os.remove(filepath) # Usuwamy tymczasowy plik

    def test_logc4_curve(self):
      self.assertTrue(np.allclose(logc4_curve(0.0), np.array([-3852.359026659536])))
      self.assertAlmostEqual(logc4_curve(0.18), 0.4090068696819821)
      self.assertTrue(np.allclose(logc4_curve(np.array([0.0, 0.18, 1.0])), np.array([-3852.359026659536, 0.4090068696819821, 0.6577136499999999])))

    def test_inverse_logc4_curve(self):
      self.assertTrue(np.allclose(inverse_logc4_curve(0.09285527796717754), np.array([0.04345044])))
      self.assertTrue(np.allclose(inverse_logc4_curve(0.4090068696819821), np.array([0.18])))
      self.assertTrue(np.allclose(inverse_logc4_curve(np.array([0.09285527796717754, 0.4090068696819821, 0.6577136499999999])), np.array([0.04345044, 0.18, 1.0])))


if __name__ == '__main__':
    unittest.main()
</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.<environment_details>
# VSCode Visible Files
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
pixelpasta/tests/test_color_analysis.py

# VSCode Open Tabs
pixelpasta/tests/test_cube_parser.py
pixelpasta/lut_processor/cube_parser.py
pixelpasta/app.py
pixelpasta/lut_processor/color_analysis.py
pixelpasta/templates/upload.html
pixelpasta/tests/test_color_analysis.py

# Current Time
19/03/2025, 6:47:05 pm (Europe/Warsaw, UTC+1:00)

# Current Mode
ACT MODE
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])))

    def test_inverse_slog3_curve(self):
        a = 0.432699
        b = 0.009468
        c = 0.655
        d = 0.037584
        e = 0.01
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])))

    def test_inverse_slog3_curve(self):
        a = 0.432699
        b = 0.009468
        c = 0.655
        d = 0.037584
        e = 0.01
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), 0.1))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), 1.0))
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), np.array([0.1])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), np.array([1.0])))
        self.assertTrue(np.allclose(inverse_slog3_curve(np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])), np.array([ (0.01 - e) / d, 0.1, 1.0])))

    def test_rec709_oetf(self):
        self.assertAlmostEqual(rec709_oetf(0.0), 0.0)
        self.assertAlmostEqual(rec709_oetf(0.018), 0.08124794403514046)
        self.assertAlmostEqual(rec709_oetf(1.0), 1.0)
        self.assertTrue(np.allclose(rec709_oetf(np.array([0.0, 0.018, 1.0])), np.array([0.0, 0.08124794403514046, 1.0])))

    def test_interpolate_1d_lut(self):
        lut_1d = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]])
        output = interpolate_1d_lut(lut_1d, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_interpolate_3d_lut(self):
        lut_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]
        ])
        lut_size = 2
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([
            [0.  , 0.  , 0.  ],
            [0.5 , 0.5 , 0.5 ],
            [1.  , 1.  , 1.  ]
        ])
        output = interpolate_3d_lut(lut_3d, lut_size, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_srgb_to_rec709(self):
        rgb_values = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        expected_output_sgamut3 = np.array([
            [ 1.641 , -0.6636,  0.0117],
            [-0.3245,  1.6157, -0.0085],
            [-0.3165,  0.0479,  0.9968]
        ])
        expected_output_sgamut3_cine = np.array([
            [ 1.5529, -0.5428, -0.0026],
            [-0.2555,  1.5027, -0.0186],
            [-0.2974,  0.0401,  1.0212]
        ])
        output_sgamut3 = srgb_to_rec709(rgb_values, 'S-Gamut3')
        output_sgamut3_cine = srgb_to_rec709(rgb_values, 'S-Gamut3.Cine')
        self.assertTrue(np.allclose(output_sgamut3, expected_output_sgamut3))
        self.assertTrue(np.allclose(output_sgamut3_cine, expected_output_sgamut3_cine))
        with self.assertRaises(ValueError):
            srgb_to_rec709(rgb_values, 'InvalidColorSpace')

    def test_generate_table(self):
        # Tworzymy tymczasowy plik .cube
        content = """
TITLE "Test LUT"
LUT_1D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as temp_file:
            temp_file.write(content.encode())
            filepath = temp_file.name

        # Testujemy dla S-Gamut3
        df_sgamut3 = generate_table(filepath, 'S-Gamut3')
        self.assertIsInstance(df_sgamut3, pd.DataFrame)
        self.assertEqual(len(df_sgamut3), 20)
        self.assertEqual(df_sgamut3['Color Space'][0], 'S-Gamut3')

        # Testujemy dla S-Gamut3.Cine
        df_sgamut3_cine = generate_table(filepath, 'S-Gamut3.Cine')
        self.assertIsInstance(df_sgamut3_cine, pd.DataFrame)
        self.assertEqual(len(df_sgamut3_cine), 20)
        self.assertEqual(df_sgamut3_cine['Color Space'][0], 'S-Gamut3.Cine')

        os.remove(filepath) # Usuwamy tymczasowy plik

    def test_logc4_curve(self):
      self.assertTrue(np.allclose(logc4_curve(0.0), np.array([-3852.359026659536])))
      self.assertAlmostEqual(logc4_curve(0.18), 0.4090068696819821)
      self.assertTrue(np.allclose(logc4_curve(np.array([0.0, 0.18, 1.0])), np.array([-3852.359026659536, 0.4090068696819821, 0.6577136499999999])))

    def test_inverse_logc4_curve(self):
      self.assertTrue(np.allclose(inverse_logc4_curve(0.09285527796717754), np.array([0.04345044])))
      self.assertTrue(np.allclose(inverse_logc4_curve(0.4090068696819821), np.array([0.18])))
      self.assertTrue(np.allclose(inverse_logc4_curve(np.array([0.09285527796717754, 0.4090068696819821, 0.6577136499999999])), np.array([0.04345044, 0.18, 1.0])))


if __name__ == '__main__':
    unittest.main()
</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.<environment_details>
# VSCode Visible Files
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
pixelpasta/tests/test_color_analysis.py

# VSCode Open Tabs
pixelpasta/tests/test_cube_parser.py
pixelpasta/lut_processor/cube_parser.py
pixelpasta/app.py
pixelpasta/lut_processor/color_analysis.py
pixelpasta/templates/upload.html
pixelpasta/tests/test_color_analysis.py

# Current Time
19/03/2025, 6:47:05 pm (Europe/Warsaw, UTC+1:00)

# Current Mode
ACT MODE
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])))

    def test_inverse_slog3_curve(self):
        a = 0.432699
        b = 0.009468
        c = 0.655
        d = 0.037584
        e = 0.01
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), np.array([0.1])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), np.array([1.0])))
        self.assertTrue(np.allclose(inverse_slog3_curve(np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])), np.array([ (0.01 - e) / d, 0.1, 1.0])))

    def test_rec709_oetf(self):
        self.assertAlmostEqual(rec709_oetf(0.0), 0.0)
        self.assertAlmostEqual(rec709_oetf(0.018), 0.08124794403514046)
        self.assertAlmostEqual(rec709_oetf(1.0), 1.0)
        self.assertTrue(np.allclose(rec709_oetf(np.array([0.0, 0.018, 1.0])), np.array([0.0, 0.08124794403514046, 1.0])))

    def test_interpolate_1d_lut(self):
        lut_1d = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]])
        output = interpolate_1d_lut(lut_1d, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_interpolate_3d_lut(self):
        lut_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]
        ])
        lut_size = 2
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([
            [0.  , 0.  , 0.  ],
            [0.5 , 0.5 , 0.5 ],
            [1.  , 1.  , 1.  ]
        ])
        output = interpolate_3d_lut(lut_3d, lut_size, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_srgb_to_rec709(self):
        rgb_values = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        expected_output_sgamut3 = np.array([
            [ 1.641 , -0.6636,  0.0117],
            [-0.3245,  1.6157, -0.0085],
            [-0.3165,  0.0479,  0.9968]
        ])
        expected_output_sgamut3_cine = np.array([
            [ 1.5529, -0.5428, -0.0026],
            [-0.2555,  1.5027, -0.0186],
            [-0.2974,  0.0401,  1.0212]
        ])
        output_sgamut3 = srgb_to_rec709(rgb_values, 'S-Gamut3')
        output_sgamut3_cine = srgb_to_rec709(rgb_values, 'S-Gamut3.Cine')
        self.assertTrue(np.allclose(output_sgamut3, expected_output_sgamut3))
        self.assertTrue(np.allclose(output_sgamut3_cine, expected_output_sgamut3_cine))
        with self.assertRaises(ValueError):
            srgb_to_rec709(rgb_values, 'InvalidColorSpace')

    def test_generate_table(self):
        # Tworzymy tymczasowy plik .cube
        content = """
TITLE "Test LUT"
LUT_1D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as temp_file:
            temp_file.write(content.encode())
            filepath = temp_file.name

        # Testujemy dla S-Gamut3
        df_sgamut3 = generate_table(filepath, 'S-Gamut3')
        self.assertIsInstance(df_sgamut3, pd.DataFrame)
        self.assertEqual(len(df_sgamut3), 20)
        self.assertEqual(df_sgamut3['Color Space'][0], 'S-Gamut3')

        # Testujemy dla S-Gamut3.Cine
        df_sgamut3_cine = generate_table(filepath, 'S-Gamut3.Cine')
        self.assertIsInstance(df_sgamut3_cine, pd.DataFrame)
        self.assertEqual(len(df_sgamut3_cine), 20)
        self.assertEqual(df_sgamut3_cine['Color Space'][0], 'S-Gamut3.Cine')

        os.remove(filepath) # Usuwamy tymczasowy plik

    def test_logc4_curve(self):
      self.assertTrue(np.allclose(logc4_curve(0.0), np.array([-3852.359026659536])))
      self.assertAlmostEqual(logc4_curve(0.18), 0.4090068696819821)
      self.assertTrue(np.allclose(logc4_curve(np.array([0.0, 0.18, 1.0])), np.array([-3852.359026659536, 0.4090068696819821, 0.6577136499999999])))

    def test_inverse_logc4_curve(self):
      self.assertTrue(np.allclose(inverse_logc4_curve(0.09285527796717754), np.array([0.04345044])))
      self.assertTrue(np.allclose(inverse_logc4_curve(0.4090068696819821), np.array([0.18])))
      self.assertTrue(np.allclose(inverse_logc4_curve(np.array([0.09285527796717754, 0.4090068696819821, 0.6577136499999999])), np.array([0.04345044, 0.18, 1.0])))


if __name__ == '__main__':
    unittest.main()
</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.<environment_details>
# VSCode Visible Files
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
pixelpasta/tests/test_color_analysis.py

# VSCode Open Tabs
pixelpasta/tests/test_cube_parser.py
pixelpasta/lut_processor/cube_parser.py
pixelpasta/app.py
pixelpasta/lut_processor/color_analysis.py
pixelpasta/templates/upload.html
pixelpasta/tests/test_color_analysis.py

# Current Time
19/03/2025, 6:47:05 pm (Europe/Warsaw, UTC+1:00)

# Current Mode
ACT MODE
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])))

    def test_inverse_slog3_curve(self):
        a = 0.432699
        b = 0.009468
        c = 0.655
        d = 0.037584
        e = 0.01
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), np.array([0.1])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), np.array([1.0])))
        self.assertTrue(np.allclose(inverse_slog3_curve(np.array([0.01, 0.432699 * np.log10(0.1
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])))

    def test_inverse_slog3_curve(self):
        a = 0.432699
        b = 0.009468
        c = 0.655
        d = 0.037584
        e = 0.01
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), 0.1))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), 1.0))
        self.assertTrue(np.allclose(inverse_slog3_curve(np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])), np.array([ (0.01 - e) / d, 0.1, 1.0])))

    def test_rec709_oetf(self):
        self.assertAlmostEqual(rec709_oetf(0.0), 0.0)
        self.assertAlmostEqual(rec709_oetf(0.018), 0.08124794403514046)
        self.assertAlmostEqual(rec709_oetf(1.0), 1.0)
        self.assertTrue(np.allclose(rec709_oetf(np.array([0.0, 0.018, 1.0])), np.array([0.0, 0.08124794403514046, 1.0])))

    def test_interpolate_1d_lut(self):
        lut_1d = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]])
        output = interpolate_1d_lut(lut_1d, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_interpolate_3d_lut(self):
        lut_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]
        ])
        lut_size = 2
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([
            [0.  , 0.  , 0.  ],
            [0.5 , 0.5 , 0.5 ],
            [1.  , 1.  , 1.  ]
        ])
        output = interpolate_3d_lut(lut_3d, lut_size, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_srgb_to_rec709(self):
        rgb_values = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        expected_output_sgamut3 = np.array([
            [ 1.641 , -0.6636,  0.0117],
            [-0.3245,  1.6157, -0.0085],
            [-0.3165,  0.0479,  0.9968]
        ])
        expected_output_sgamut3_cine = np.array([
            [ 1.5529, -0.5428, -0.0026],
            [-0.2555,  1.5027, -0.0186],
            [-0.2974,  0.0401,  1.0212]
        ])
        output_sgamut3 = srgb_to_rec709(rgb_values, 'S-Gamut3')
        output_sgamut3_cine = srgb_to_rec709(rgb_values, 'S-Gamut3.Cine')
        self.assertTrue(np.allclose(output_sgamut3, expected_output_sgamut3))
        self.assertTrue(np.allclose(output_sgamut3_cine, expected_output_sgamut3_cine))
        with self.assertRaises(ValueError):
            srgb_to_rec709(rgb_values, 'InvalidColorSpace')

    def test_generate_table(self):
        # Tworzymy tymczasowy plik .cube
        content = """
TITLE "Test LUT"
LUT_1D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as temp_file:
            temp_file.write(content.encode())
            filepath = temp_file.name

        # Testujemy dla S-Gamut3
        df_sgamut3 = generate_table(filepath, 'S-Gamut3')
        self.assertIsInstance(df_sgamut3, pd.DataFrame)
        self.assertEqual(len(df_sgamut3), 20)
        self.assertEqual(df_sgamut3['Color Space'][0], 'S-Gamut3')

        # Testujemy dla S-Gamut3.Cine
        df_sgamut3_cine = generate_table(filepath, 'S-Gamut3.Cine')
        self.assertIsInstance(df_sgamut3_cine, pd.DataFrame)
        self.assertEqual(len(df_sgamut3_cine), 20)
        self.assertEqual(df_sgamut3_cine['Color Space'][0], 'S-Gamut3.Cine')

        os.remove(filepath) # Usuwamy tymczasowy plik

    def test_logc4_curve(self):
      self.assertTrue(np.allclose(logc4_curve(0.0), np.array([-3852.359026659536])))
      self.assertAlmostEqual(logc4_curve(0.18), 0.4090068696819821)
      self.assertTrue(np.allclose(logc4_curve(np.array([0.0, 0.18, 1.0])), np.array([-3852.359026659536, 0.4090068696819821, 0.6577136499999999])))

    def test_inverse_logc4_curve(self):
      self.assertTrue(np.allclose(inverse_logc4_curve(0.09285527796717754), np.array([0.04345044])))
      self.assertTrue(np.allclose(inverse_logc4_curve(0.4090068696819821), np.array([0.18])))
      self.assertTrue(np.allclose(inverse_logc4_curve(np.array([0.09285527796717754, 0.4090068696819821, 0.6577136499999999])), np.array([0.04345044, 0.18, 1.0])))


if __name__ == '__main__':
    unittest.main()
</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.<environment_details>
# VSCode Visible Files
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
pixelpasta/tests/test_color_analysis.py

# VSCode Open Tabs
pixelpasta/tests/test_cube_parser.py
pixelpasta/lut_processor/cube_parser.py
pixelpasta/app.py
pixelpasta/lut_processor/color_analysis.py
pixelpasta/templates/upload.html
pixelpasta/tests/test_color_analysis.py

# Current Time
19/03/2025, 6:47:05 pm (Europe/Warsaw, UTC+1:00)

# Current Mode
ACT MODE
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])))

    def test_inverse_slog3_curve(self):
        a = 0.432699
        b = 0.009468
        c = 0.655
        d = 0.037584
        e = 0.01
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), np.array([0.1])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), np.array([1.0])))
        self.assertTrue(np.allclose(inverse_slog3_curve(np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])), np.array([ (0.01 - e) / d, 0.1, 1.0])))

    def test_rec709_oetf(self):
        self.assertAlmostEqual(rec709_oetf(0.0), 0.0)
        self.assertAlmostEqual(rec709_oetf(0.018), 0.08124794403514046)
        self.assertAlmostEqual(rec709_oetf(1.0), 1.0)
        self.assertTrue(np.allclose(rec709_oetf(np.array([0.0, 0.018, 1.0])), np.array([0.0, 0.08124794403514046, 1.0])))

    def test_interpolate_1d_lut(self):
        lut_1d = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]])
        output = interpolate_1d_lut(lut_1d, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_interpolate_3d_lut(self):
        lut_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]
        ])
        lut_size = 2
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([
            [0.  , 0.  , 0.  ],
            [0.5 , 0.5 , 0.5 ],
            [1.  , 1.  , 1.  ]
        ])
        output = interpolate_3d_lut(lut_3d, lut_size, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_srgb_to_rec709(self):
        rgb_values = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        expected_output_sgamut3 = np.array([
            [ 1.641 , -0.6636,  0.0117],
            [-0.3245,  1.6157, -0.0085],
            [-0.3165,  0.0479,  0.9968]
        ])
        expected_output_sgamut3_cine = np.array([
            [ 1.5529, -0.5428, -0.0026],
            [-0.2555,  1.5027, -0.0186],
            [-0.2974,  0.0401,  1.0212]
        ])
        output_sgamut3 = srgb_to_rec709(rgb_values, 'S-Gamut3')
        output_sgamut3_cine = srgb_to_rec709(rgb_values, 'S-Gamut3.Cine')
        self.assertTrue(np.allclose(output_sgamut3, expected_output_sgamut3))
        self.assertTrue(np.allclose(output_sgamut3_cine, expected_output_sgamut3_cine))
        with self.assertRaises(ValueError):
            srgb_to_rec709(rgb_values, 'InvalidColorSpace')

    def test_generate_table(self):
        # Tworzymy tymczasowy plik .cube
        content = """
TITLE "Test LUT"
LUT_1D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as temp_file:
            temp_file.write(content.encode())
            filepath = temp_file.name

        # Testujemy dla S-Gamut3
        df_sgamut3 = generate_table(filepath, 'S-Gamut3')
        self.assertIsInstance(df_sgamut3, pd.DataFrame)
        self.assertEqual(len(df_sgamut3), 20)
        self.assertEqual(df_sgamut3['Color Space'][0], 'S-Gamut3')

        # Testujemy dla S-Gamut3.Cine
        df_sgamut3_cine = generate_table(filepath, 'S-Gamut3.Cine')
        self.assertIsInstance(df_sgamut3_cine, pd.DataFrame)
        self.assertEqual(len(df_sgamut3_cine), 20)
        self.assertEqual(df_sgamut3_cine['Color Space'][0], 'S-Gamut3.Cine')

        os.remove(filepath) # Usuwamy tymczasowy plik

    def test_logc4_curve(self):
      self.assertTrue(np.allclose(logc4_curve(0.0), np.array([-3852.359026659536])))
      self.assertAlmostEqual(logc4_curve(0.18), 0.4090068696819821)
      self.assertTrue(np.allclose(logc4_curve(np.array([0.0, 0.18, 1.0])), np.array([-3852.359026659536, 0.4090068696819821, 0.6577136499999999])))

    def test_inverse_logc4_curve(self):
      self.assertTrue(np.allclose(inverse_logc4_curve(0.09285527796717754), np.array([0.04345044])))
      self.assertTrue(np.allclose(inverse_logc4_curve(0.4090068696819821), np.array([0.18])))
      self.assertTrue(np.allclose(inverse_logc4_curve(np.array([0.09285527796717754, 0.4090068696819821, 0.6577136499999999])), np.array([0.04345044, 0.18, 1.0])))


if __name__ == '__main__':
    unittest.main()
</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.<environment_details>
# VSCode Visible Files
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
pixelpasta/tests/test_color_analysis.py

# VSCode Open Tabs
pixelpasta/tests/test_cube_parser.py
pixelpasta/lut_processor/cube_parser.py
pixelpasta/app.py
pixelpasta/lut_processor/color_analysis.py
pixelpasta/templates/upload.html
pixelpasta/tests/test_color_analysis.py

# Current Time
19/03/2025, 6:47:05 pm (Europe/Warsaw, UTC+1:00)

# Current Mode
ACT MODE
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) +
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])))

    def test_inverse_slog3_curve(self):
        a = 0.432699
        b = 0.009468
        c = 0.655
        d = 0.037584
        e = 0.01
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), np.array([0.1])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), np.array([1.0])))
        self.assertTrue(np.allclose(inverse_slog3_curve(np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])), np.array([ (0.01 - e) / d, 0.1, 1.0])))

    def test_rec709_oetf(self):
        self.assertAlmostEqual(rec709_oetf(0.0), 0.0)
        self.assertAlmostEqual(rec709_oetf(0.018), 0.08124794403514046)
        self.assertAlmostEqual(rec709_oetf(1.0), 1.0)
        self.assertTrue(np.allclose(rec709_oetf(np.array([0.0, 0.018, 1.0])), np.array([0.0, 0.08124794403514046, 1.0])))

    def test_interpolate_1d_lut(self):
        lut_1d = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]])
        output = interpolate_1d_lut(lut_1d, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_interpolate_3d_lut(self):
        lut_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]
        ])
        lut_size = 2
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([
            [0.  , 0.  , 0.  ],
            [0.5 , 0.5 , 0.5 ],
            [1.  , 1.  , 1.  ]
        ])
        output = interpolate_3d_lut(lut_3d, lut_size, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_srgb_to_rec709(self):
        rgb_values = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        expected_output_sgamut3 = np.array([
            [ 1.641 , -0.6636,  0.0117],
            [-0.3245,  1.6157, -0.0085],
            [-0.3165,  0.0479,  0.9968]
        ])
        expected_output_sgamut3_cine = np.array([
            [ 1.5529, -0.5428, -0.0026],
            [-0.2555,  1.5027, -0.0186],
            [-0.2974,  0.0401,  1.0212]
        ])
        output_sgamut3 = srgb_to_rec709(rgb_values, 'S-Gamut3')
        output_sgamut3_cine = srgb_to_rec709(rgb_values, 'S-Gamut3.Cine')
        self.assertTrue(np.allclose(output_sgamut3, expected_output_sgamut3))
        self.assertTrue(np.allclose(output_sgamut3_cine, expected_output_sgamut3_cine))
        with self.assertRaises(ValueError):
            srgb_to_rec709(rgb_values, 'InvalidColorSpace')

    def test_generate_table(self):
        # Tworzymy tymczasowy plik .cube
        content = """
TITLE "Test LUT"
LUT_1D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as temp_file:
            temp_file.write(content.encode())
            filepath = temp_file.name

        # Testujemy dla S-Gamut3
        df_sgamut3 = generate_table(filepath, 'S-Gamut3')
        self.assertIsInstance(df_sgamut3, pd.DataFrame)
        self.assertEqual(len(df_sgamut3), 20)
        self.assertEqual(df_sgamut3['Color Space'][0], 'S-Gamut3')

        # Testujemy dla S-Gamut3.Cine
        df_sgamut3_cine = generate_table(filepath, 'S-Gamut3.Cine')
        self.assertIsInstance(df_sgamut3_cine, pd.DataFrame)
        self.assertEqual(len(df_sgamut3_cine), 20)
        self.assertEqual(df_sgamut3_cine['Color Space'][0], 'S-Gamut3.Cine')

        os.remove(filepath) # Usuwamy tymczasowy plik

    def test_logc4_curve(self):
      self.assertTrue(np.allclose(logc4_curve(0.0), np.array([-3852.359026659536])))
      self.assertAlmostEqual(logc4_curve(0.18), 0.4090068696819821)
      self.assertTrue(np.allclose(logc4_curve(np.array([0.0, 0.18, 1.0])), np.array([-3852.359026659536, 0.4090068696819821, 0.6577136499999999])))

    def test_inverse_logc4_curve(self):
      self.assertTrue(np.allclose(inverse_logc4_curve(0.09285527796717754), np.array([0.04345044])))
      self.assertTrue(np.allclose(inverse_logc4_curve(0.4090068696819821), np.array([0.18])))
      self.assertTrue(np.allclose(inverse_logc4_curve(np.array([0.09285527796717754, 0.4090068696819821, 0.6577136499999999])), np.array([0.04345044, 0.18, 1.0])))


if __name__ == '__main__':
    unittest.main()
</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.<environment_details>
# VSCode Visible Files
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
pixelpasta/tests/test_color_analysis.py

# VSCode Open Tabs
pixelpasta/tests/test_cube_parser.py
pixelpasta/lut_processor/cube_parser.py
pixelpasta/app.py
pixelpasta/lut_processor/color_analysis.py
pixelpasta/templates/upload.html
pixelpasta/tests/test_color_analysis.py

# Current Time
19/03/2025, 6:47:05 pm (Europe/Warsaw, UTC+1:00)

# Current Mode
ACT MODE
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])))

    def test_inverse_slog3_curve(self):
        a = 0.432699
        b = 0.009468
        c = 0.655
        d = 0.037584
        e = 0.01
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), np.array([0.1])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), np.array([1.0])))
        self.assertTrue(np.allclose(inverse_slog3_curve(np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])), np.array([ (0.01 - e) / d, 0.1, 1.0])))

    def test_rec709_oetf(self):
        self.assertAlmostEqual(rec709_oetf(0.0), 0.0)
        self.assertAlmostEqual(rec709_oetf(0.018), 0.08124794403514046)
        self.assertAlmostEqual(rec709_oetf(1.0), 1.0)
        self.assertTrue(np.allclose(rec709_oetf(np.array([0.0, 0.018, 1.0])), np.array([0.0, 0.08124794403514046, 1.0])))

    def test_interpolate_1d_lut(self):
        lut_1d = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]])
        output = interpolate_1d_lut(lut_1d, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_interpolate_3d_lut(self):
        lut_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]
        ])
        lut_size = 2
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([
            [0.  , 0.  , 0.  ],
            [0.5 , 0.5 , 0.5 ],
            [1.  , 1.  , 1.  ]
        ])
        output = interpolate_3d_lut(lut_3d, lut_size, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_srgb_to_rec709(self):
        rgb_values = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        expected_output_sgamut3 = np.array([
            [ 1.641 , -0.6636,  0.0117],
            [-0.3245,  1.6157, -0.0085],
            [-0.3165,  0.0479,  0.9968]
        ])
        expected_output_sgamut3_cine = np.array([
            [ 1.5529, -0.5428, -0.0026],
            [-0.2555,  1.5027, -0.0186],
            [-0.2974,  0.0401,  1.0212]
        ])
        output_sgamut3 = srgb_to_rec709(rgb_values, 'S-Gamut3')
        output_sgamut3_cine = srgb_to_rec709(rgb_values, 'S-Gamut3.Cine')
        self.assertTrue(np.allclose(output_sgamut3, expected_output_sgamut3))
        self.assertTrue(np.allclose(output_sgamut3_cine, expected_output_sgamut3_cine))
        with self.assertRaises(ValueError):
            srgb_to_rec709(rgb_values, 'InvalidColorSpace')

    def test_generate_table(self):
        # Tworzymy tymczasowy plik .cube
        content = """
TITLE "Test LUT"
LUT_1D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as temp_file:
            temp_file.write(content.encode())
            filepath = temp_file.name

        # Testujemy dla S-Gamut3
        df_sgamut3 = generate_table(filepath, 'S-Gamut3')
        self.assertIsInstance(df_sgamut3, pd.DataFrame)
        self.assertEqual(len(df_sgamut3), 20)
        self.assertEqual(df_sgamut3['Color Space'][0], 'S-Gamut3')

        # Testujemy dla S-Gamut3.Cine
        df_sgamut3_cine = generate_table(filepath, 'S-Gamut3.Cine')
        self.assertIsInstance(df_sgamut3_cine, pd.DataFrame)
        self.assertEqual(len(df_sgamut3_cine), 20)
        self.assertEqual(df_sgamut3_cine['Color Space'][0], 'S-Gamut3.Cine')

        os.remove(filepath) # Usuwamy tymczasowy plik

    def test_logc4_curve(self):
      self.assertTrue(np.allclose(logc4_curve(0.0), np.array([-3852.359026659536])))
      self.assertAlmostEqual(logc4_curve(0.18), 0.4090068696819821)
      self.assertTrue(np.allclose(logc4_curve(np.array([0.0, 0.18, 1.0])), np.array([-3852.359026659536, 0.4090068696819821, 0.6577136499999999])))

    def test_inverse_logc4_curve(self):
      self.assertTrue(np.allclose(inverse_logc4_curve(0.09285527796717754), np.array([0.04345044])))
      self.assertTrue(np.allclose(inverse_logc4_curve(0.4090068696819821), np.array([0.18])))
      self.assertTrue(np.allclose(inverse_logc4_curve(np.array([0.09285527796717754, 0.4090068696819821, 0.6577136499999999])), np.array([0.04345044, 0.18, 1.0])))


if __name__ == '__main__':
    unittest.main()
</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.<environment_details>
# VSCode Visible Files
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
pixelpasta/tests/test_color_analysis.py

# VSCode Open Tabs
pixelpasta/tests/test_cube_parser.py
pixelpasta/lut_processor/cube_parser.py
pixelpasta/app.py
pixelpasta/lut_processor/color_analysis.py
pixelpasta/templates/upload.html
pixelpasta/tests/test_color_analysis.py

# Current Time
19/03/2025, 6:47:05 pm (Europe/Warsaw, UTC+1:00)

# Current Mode
ACT MODE
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])))

    def test_inverse_slog3_curve(self):
        a = 0.432699
        b = 0.009468
        c = 0.655
        d = 0.037584
        e = 0.01
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), np.array([0.1])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), np.array([1.0])))
        self.assertTrue(np.allclose(inverse_slog3_curve(np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])), np.array([ (0.01 - e) / d, 0.1, 1.0])))

    def test_rec709_oetf(self):
        self.assertAlmostEqual(rec709_oetf(0.0), 0.0)
        self.assertAlmostEqual(rec709_oetf(0.018), 0.08124794403514046)
        self.assertAlmostEqual(rec709_oetf(1.0), 1.0)
        self.assertTrue(np.allclose(rec709_oetf(np.array([0.0, 0.018, 1.0])), np.array([0.0, 0.08124794403514046, 1.0])))

    def test_interpolate_1d_lut(self):
        lut_1d = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]])
        output = interpolate_1d_lut(lut_1d, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_interpolate_3d_lut(self):
        lut_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]
        ])
        lut_size = 2
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([
            [0.  , 0.  , 0.  ],
            [0.5 , 0.5 , 0.5 ],
            [1.  , 1.  , 1.  ]
        ])
        output = interpolate_3d_lut(lut_3d, lut_size, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_srgb_to_rec709(self):
        rgb_values = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        expected_output_sgamut3 = np.array([
            [ 1.641 , -0.6636,  0.0117],
            [-0.3245,  1.6157, -0.0085],
            [-0.3165,  0.0479,  0.9968]
        ])
        expected_output_sgamut3_cine = np.array([
            [ 1.5529, -0.5428, -0.0026],
            [-0.2555,  1.5027, -0.0186],
            [-0.2974,  0.0401,  1.0212]
        ])
        output_sgamut3 = srgb_to_rec709(rgb_values, 'S-Gamut3')
        output_sgamut3_cine = srgb_to_rec709(rgb_values, 'S-Gamut3.Cine')
        self.assertTrue(np.allclose(output_sgamut3, expected_output_sgamut3))
        self.assertTrue(np.allclose(output_sgamut3_cine, expected_output_sgamut3_cine))
        with self.assertRaises(ValueError):
            srgb_to_rec709(rgb_values, 'InvalidColorSpace')

    def test_generate_table(self):
        # Tworzymy tymczasowy plik .cube
        content = """
TITLE "Test LUT"
LUT_1D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as temp_file:
            temp_file.write(content.encode())
            filepath = temp_file.name

        # Testujemy dla S-Gamut3
        df_sgamut3 = generate_table(filepath, 'S-Gamut3')
        self.assertIsInstance(df_sgamut3, pd.DataFrame)
        self.assertEqual(len(df_sgamut3), 20)
        self.assertEqual(df_sgamut3['Color Space'][0], 'S-Gamut3')

        # Testujemy dla S-Gamut3.Cine
        df_sgamut3_cine = generate_table(filepath, 'S-Gamut3.Cine')
        self.assertIsInstance(df_sgamut3_cine, pd.DataFrame)
        self.assertEqual(len(df_sgamut3_cine), 20)
        self.assertEqual(df_sgamut3_cine['Color Space'][0], 'S-Gamut3.Cine')

        os.remove(filepath) # Usuwamy tymczasowy plik

    def test_logc4_curve(self):
      self.assertTrue(np.allclose(logc4_curve(0.0), np.array([-3852.359026659536])))
      self.assertAlmostEqual(logc4_curve(0.18), 0.4090068696819821)
      self.assertTrue(np.allclose(logc4_curve(np.array([0.0, 0.18, 1.0])), np.array([-3852.359026659536, 0.4090068696819821, 0.6577136499999999])))

    def test_inverse_logc4_curve(self):
      self.assertTrue(np.allclose(inverse_logc4_curve(0.09285527796717754), np.array([0.04345044])))
      self.assertTrue(np.allclose(inverse_logc4_curve(0.4090068696819821), np.array([0.18])))
      self.assertTrue(np.allclose(inverse_logc4_curve(np.array([0.09285527796717754, 0.4090068696819821, 0.6577136499999999])), np.array([0.04345044, 0.18, 1.0])))


if __name__ == '__main__':
    unittest.main()
</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.<environment_details>
# VSCode Visible Files
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
pixelpasta/tests/test_color_analysis.py

# VSCode Open Tabs
pixelpasta/tests/test_cube_parser.py
pixelpasta/lut_processor/cube_parser.py
pixelpasta/app.py
pixelpasta/lut_processor/color_analysis.py
pixelpasta/templates/upload.html
pixelpasta/tests/test_color_analysis.py

# Current Time
19/03/2025, 6:47:05 pm (Europe/Warsaw, UTC+1:00)

# Current Mode
ACT MODE
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])))

    def test_inverse_slog3_curve(self):
        a = 0.432699
        b = 0.009468
        c = 0.655
        d = 0.037584
        e = 0.01
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), np.array([0.1])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), np.array([1.0])))
        self.assertTrue(np.allclose(inverse_slog3_curve(np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])), np.array([ (0.01 - e) / d, 0.1, 1.0])))

    def test_rec709_oetf(self):
        self.assertAlmostEqual(rec709_oetf(0.0), 0.0)
        self.assertAlmostEqual(rec709_oetf(0.018), 0.08124794403514046)
        self.assertAlmostEqual(rec709_oetf(1.0), 1.0)
        self.assertTrue(np.allclose(rec709_oetf(np.array([0.0, 0.018, 1.0])), np.array([0.0, 0.08124794403514046, 1.0])))

    def test_interpolate_1d_lut(self):
        lut_1d = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]])
        output = interpolate_1d_lut(lut_1d, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_interpolate_3d_lut(self):
        lut_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]
        ])
        lut_size = 2
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([
            [0.  , 0.  , 0.  ],
            [0.5 , 0.5 , 0.5 ],
            [1.  , 1.  , 1.  ]
        ])
        output = interpolate_3d_lut(lut_3d, lut_size, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_srgb_to_rec709(self):
        rgb_values = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        expected_output_sgamut3 = np.array([
            [ 1.641 , -0.6636,  0.0117],
            [-0.3245,  1.6157, -0.0085],
            [-0.3165,  0.0479,  0.9968]
        ])
        expected_output_sgamut3_cine = np.array([
            [ 1.5529, -0.5428, -0.0026],
            [-0.2555,  1.5027, -0.0186],
            [-0.2974,  0.0401,  1.0212]
        ])
        output_sgamut3 = srgb_to_rec709(rgb_values, 'S-Gamut3')
        output_sgamut3_cine = srgb_to_rec709(rgb_values, 'S-Gamut3.Cine')
        self.assertTrue(np.allclose(output_sgamut3, expected_output_sgamut3))
        self.assertTrue(np.allclose(output_sgamut3_cine, expected_output_sgamut3_cine))
        with self.assertRaises(ValueError):
            srgb_to_rec709(rgb_values, 'InvalidColorSpace')

    def test_generate_table(self):
        # Tworzymy tymczasowy plik .cube
        content = """
TITLE "Test LUT"
LUT_1D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as temp_file:
            temp_file.write(content.encode())
            filepath = temp_file.name

        # Testujemy dla S-Gamut3
        df_sgamut3 = generate_table(filepath, 'S-Gamut3')
        self.assertIsInstance(df_sgamut3, pd.DataFrame)
        self.assertEqual(len(df_sgamut3), 20)
        self.assertEqual(df_sgamut3['Color Space'][0], 'S-Gamut3')

        # Testujemy dla S-Gamut3.Cine
        df_sgamut3_cine = generate_table(filepath, 'S-Gamut3.Cine')
        self.assertIsInstance(df_sgamut3_cine, pd.DataFrame)
        self.assertEqual(len(df_sgamut3_cine), 20)
        self.assertEqual(df_sgamut3_cine['Color Space'][0], 'S-Gamut3.Cine')

        os.remove(filepath) # Usuwamy tymczasowy plik

    def test_logc4_curve(self):
      self.assertTrue(np.allclose(logc4_curve(0.0), np.array([-3852.359026659536])))
      self.assertAlmostEqual(logc4_curve(0.18), 0.4090068696819821)
      self.assertTrue(np.allclose(logc4_curve(np.array([0.0, 0.18, 1.0])), np.array([-3852.359026659536, 0.4090068696819821, 0.6577136499999999])))

    def test_inverse_logc4_curve(self):
      self.assertTrue(np.allclose(inverse_logc4_curve(0.09285527796717754), np.array([0.04345044])))
      self.assertTrue(np.allclose(inverse_logc4_curve(0.4090068696819821), np.array([0.18])))
      self.assertTrue(np.allclose(inverse_logc4_curve(np.array([0.09285527796717754, 0.4090068696819821, 0.6577136499999999])), np.array([0.04345044, 0.18, 1.0])))


if __name__ == '__main__':
    unittest.main()
</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.<environment_details>
# VSCode Visible Files
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
pixelpasta/tests/test_color_analysis.py

# VSCode Open Tabs
pixelpasta/tests/test_cube_parser.py
pixelpasta/lut_processor/cube_parser.py
pixelpasta/app.py
pixelpasta/lut_processor/color_analysis.py
pixelpasta/templates/upload.html
pixelpasta/tests/test_color_analysis.py

# Current Time
19/03/2025, 6:47:05 pm (Europe/Warsaw, UTC+1:00)

# Current Mode
ACT MODE
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])))

    def test_inverse_slog3_curve(self):
        a = 0.432699
        b = 0.009468
        c = 0.655
        d = 0.037584
        e = 0.01
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), np.array([0.1])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), np.array([1.0])))
        self.assertTrue(np.allclose(inverse_slog3_curve(np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])), np.array([ (0.01 - e) / d, 0.1, 1.0])))

    def test_rec709_oetf(self):
        self.assertAlmostEqual(rec709_oetf(0.0), 0.0)
        self.assertAlmostEqual(rec709_oetf(0.018), 0.08124794403514046)
        self.assertAlmostEqual(rec709_oetf(1.0), 1.0)
        self.assertTrue(np.allclose(rec709_oetf(np.array([0.0, 0.018, 1.0])), np.array([0.0, 0.08124794403514046, 1.0])))

    def test_interpolate_1d_lut(self):
        lut_1d = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]])
        output = interpolate_1d_lut(lut_1d, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_interpolate_3d_lut(self):
        lut_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]
        ])
        lut_size = 2
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([
            [0.  , 0.  , 0.  ],
            [0.5 , 0.5 , 0.5 ],
            [1.  , 1.  , 1.  ]
        ])
        output = interpolate_3d_lut(lut_3d, lut_size, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_srgb_to_rec709(self):
        rgb_values = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        expected_output_sgamut3 = np.array([
            [ 1.641 , -0.6636,  0.0117],
            [-0.3245,  1.6157, -0.0085],
            [-0.3165,  0.0479,  0.9968]
        ])
        expected_output_sgamut3_cine = np.array([
            [ 1.5529, -0.5428, -0.0026],
            [-0.2555,  1.5027, -0.0186],
            [-0.2974,  0.0401,  1.0212]
        ])
        output_sgamut3 = srgb_to_rec709(rgb_values, 'S-Gamut3')
        output_sgamut3_cine = srgb_to_rec709(rgb_values, 'S-Gamut3.Cine')
        self.assertTrue(np.allclose(output_sgamut3, expected_output_sgamut3))
        self.assertTrue(np.allclose(output_sgamut3_cine, expected_output_sgamut3_cine))
        with self.assertRaises(ValueError):
            srgb_to_rec709(rgb_values, 'InvalidColorSpace')

    def test_generate_table(self):
        # Tworzymy tymczasowy plik .cube
        content = """
TITLE "Test LUT"
LUT_1D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as temp_file:
            temp_file.write(content.encode())
            filepath = temp_file.name

        # Testujemy dla S-Gamut3
        df_sgamut3 = generate_table(filepath, 'S-Gamut3')
        self.assertIsInstance(df_sgamut3, pd.DataFrame)
        self.assertEqual(len(df_sgamut3), 20)
        self.assertEqual(df_sgamut3['Color Space'][0], 'S-Gamut3')

        # Testujemy dla S-Gamut3.Cine
        df_sgamut3_cine = generate_table(filepath, 'S-Gamut3.Cine')
        self.assertIsInstance(df_sgamut3_cine, pd.DataFrame)
        self.assertEqual(len(df_sgamut3_cine), 20)
        self.assertEqual(df_sgamut3_cine['Color Space'][0], 'S-Gamut3.Cine')

        os.remove(filepath) # Usuwamy tymczasowy plik

    def test_logc4_curve(self):
      self.assertTrue(np.allclose(logc4_curve(0.0), np.array([-3852.359026659536])))
      self.assertAlmostEqual(logc4_curve(0.18), 0.4090068696819821)
      self.assertTrue(np.allclose(logc4_curve(np.array([0.0, 0.18, 1.0])), np.array([-3852.359026659536, 0.4090068696819821, 0.6577136499999999])))

    def test_inverse_logc4_curve(self):
      self.assertTrue(np.allclose(inverse_logc4_curve(0.09285527796717754), np.array([0.04345044])))
      self.assertTrue(np.allclose(inverse_logc4_curve(0.4090068696819821), np.array([0.18])))
      self.assertTrue(np.allclose(inverse_logc4_curve(np.array([0.09285527796717754, 0.4090068696819821, 0.6577136499999999])), np.array([0.04345044, 0.18, 1.0])))


if __name__ == '__main__':
    unittest.main()
</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.<environment_details>
# VSCode Visible Files
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
pixelpasta/tests/test_color_analysis.py

# VSCode Open Tabs
pixelpasta/tests/test_cube_parser.py
pixelpasta/lut_processor/cube_parser.py
pixelpasta/app.py
pixelpasta/lut_processor/color_analysis.py
pixelpasta/templates/upload.html
pixelpasta/tests/test_color_analysis.py

# Current Time
19/03/2025, 6:47:05 pm (Europe/Warsaw, UTC+1:00)

# Current Mode
ACT MODE
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])))

    def test_inverse_slog3_curve(self):
        a = 0.432699
        b = 0.009468
        c = 0.655
        d = 0.037584
        e = 0.01
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), np.array([0.1])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), np.array([1.0])))
        self.assertTrue(np.allclose(inverse_slog3_curve(np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])), np.array([ (0.01 - e) / d, 0.1, 1.0])))

    def test_rec709_oetf(self):
        self.assertAlmostEqual(rec709_oetf(0.0), 0.0)
        self.assertAlmostEqual(rec709_oetf(0.018), 0.08124794403514046)
        self.assertAlmostEqual(rec709_oetf(1.0), 1.0)
        self.assertTrue(np.allclose(rec709_oetf(np.array([0.0, 0.018, 1.0])), np.array([0.0, 0.08124794403514046, 1.0])))

    def test_interpolate_1d_lut(self):
        lut_1d = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]])
        output = interpolate_1d_lut(lut_1d, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_interpolate_3d_lut(self):
        lut_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]
        ])
        lut_size = 2
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([
            [0.  , 0.  , 0.  ],
            [0.5 , 0.5 , 0.5 ],
            [1.  , 1.  , 1.  ]
        ])
        output = interpolate_3d_lut(lut_3d, lut_size, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_srgb_to_rec709(self):
        rgb_values = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        expected_output_sgamut3 = np.array([
            [ 1.641 , -0.6636,  0.0117],
            [-0.3245,  1.6157, -0.0085],
            [-0.3165,  0.0479,  0.9968]
        ])
        expected_output_sgamut3_cine = np.array([
            [ 1.5529, -0.5428, -0.0026],
            [-0.2555,  1.5027, -0.0186],
            [-0.2974,  0.0401,  1.0212]
        ])
        output_sgamut3 = srgb_to_rec709(rgb_values, 'S-Gamut3')
        output_sgamut3_cine = srgb_to_rec709(rgb_values, 'S-Gamut3.Cine')
        self.assertTrue(np.allclose(output_sgamut3, expected_output_sgamut3))
        self.assertTrue(np.allclose(output_sgamut3_cine, expected_output_sgamut3_cine))
        with self.assertRaises(ValueError):
            srgb_to_rec709(rgb_values, 'InvalidColorSpace')

    def test_generate_table(self):
        # Tworzymy tymczasowy plik .cube
        content = """
TITLE "Test LUT"
LUT_1D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as temp_file:
            temp_file.write(content.encode())
            filepath = temp_file.name

        # Testujemy dla S-Gamut3
        df_sgamut3 = generate_table(filepath, 'S-Gamut3')
        self.assertIsInstance(df_sgamut3, pd.DataFrame)
        self.assertEqual(len(df_sgamut3), 20)
        self.assertEqual(df_sgamut3['Color Space'][0], 'S-Gamut3')

        # Testujemy dla S-Gamut3.Cine
        df_sgamut3_cine = generate_table(filepath, 'S-Gamut3.Cine')
        self.assertIsInstance(df_sgamut3_cine, pd.DataFrame)
        self.assertEqual(len(df_sgamut3_cine), 20)
        self.assertEqual(df_sgamut3_cine['Color Space'][0], 'S-Gamut3.Cine')

        os.remove(filepath) # Usuwamy tymczasowy plik

    def test_logc4_curve(self):
      self.assertTrue(np.allclose(logc4_curve(0.0), np.array([-3852.359026659536])))
      self.assertAlmostEqual(logc4_curve(0.18), 0.4090068696819821)
      self.assertTrue(np.allclose(logc4_curve(np.array([0.0, 0.18, 1.0])), np.array([-3852.359026659536, 0.4090068696819821, 0.6577136499999999])))

    def test_inverse_logc4_curve(self):
      self.assertTrue(np.allclose(inverse_logc4_curve(0.09285527796717754), np.array([0.04345044])))
      self.assertTrue(np.allclose(inverse_logc4_curve(0.4090068696819821), np.array([0.18])))
      self.assertTrue(np.allclose(inverse_logc4_curve(np.array([0.09285527796717754, 0.4090068696819821, 0.6577136499999999])), np.array([0.04345044, 0.18, 1.0])))


if __name__ == '__main__':
    unittest.main()
</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.<environment_details>
# VSCode Visible Files
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
pixelpasta/tests/test_color_analysis.py

# VSCode Open Tabs
pixelpasta/tests/test_cube_parser.py
pixelpasta/lut_processor/cube_parser.py
pixelpasta/app.py
pixelpasta/lut_processor/color_analysis.py
pixelpasta/templates/upload.html
pixelpasta/tests/test_color_analysis.py

# Current Time
19/03/2025, 6:47:05 pm (Europe/Warsaw, UTC+1:00)

# Current Mode
ACT MODE
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])))

    def test_inverse_slog3_curve(self):
        a = 0.432699
        b = 0.009468
        c = 0.655
        d = 0.037584
        e = 0.01
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), np.array([0.1])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), np.array([1.0])))
        self.assertTrue(np.allclose(inverse_slog3_curve(np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])), np.array([ (0.01 - e) / d, 0.1, 1.0])))

    def test_rec709_oetf(self):
        self.assertAlmostEqual(rec709_oetf(0.0), 0.0)
        self.assertAlmostEqual(rec709_oetf(0.018), 0.08124794403514046)
        self.assertAlmostEqual(rec709_oetf(1.0), 1.0)
        self.assertTrue(np.allclose(rec709_oetf(np.array([0.0, 0.018, 1.0])), np.array([0.0, 0.08124794403514046, 1.0])))

    def test_interpolate_1d_lut(self):
        lut_1d = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]])
        output = interpolate_1d_lut(lut_1d, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_interpolate_3d_lut(self):
        lut_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]
        ])
        lut_size = 2
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([
            [0.  , 0.  , 0.  ],
            [0.5 , 0.5 , 0.5 ],
            [1.  , 1.  , 1.  ]
        ])
        output = interpolate_3d_lut(lut_3d, lut_size, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_srgb_to_rec709(self):
        rgb_values = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        expected_output_sgamut3 = np.array([
            [ 1.641 , -0.6636,  0.0117],
            [-0.3245,  1.6157, -0.0085],
            [-0.3165,  0.0479,  0.9968]
        ])
        expected_output_sgamut3_cine = np.array([
            [ 1.5529, -0.5428, -0.0026],
            [-0.2555,  1.5027, -0.0186],
            [-0.2974,  0.0401,  1.0212]
        ])
        output_sgamut3 = srgb_to_rec709(rgb_values, 'S-Gamut3')
        output_sgamut3_cine = srgb_to_rec709(rgb_values, 'S-Gamut3.Cine')
        self.assertTrue(np.allclose(output_sgamut3, expected_output_sgamut3))
        self.assertTrue(np.allclose(output_sgamut3_cine, expected_output_sgamut3_cine))
        with self.assertRaises(ValueError):
            srgb_to_rec709(rgb_values, 'InvalidColorSpace')

    def test_generate_table(self):
        # Tworzymy tymczasowy plik .cube
        content = """
TITLE "Test LUT"
LUT_1D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as temp_file:
            temp_file.write(content.encode())
            filepath = temp_file.name

        # Testujemy dla S-Gamut3
        df_sgamut3 = generate_table(filepath, 'S-Gamut3')
        self.assertIsInstance(df_sgamut3, pd.DataFrame)
        self.assertEqual(len(df_sgamut3), 20)
        self.assertEqual(df_sgamut3['Color Space'][0], 'S-Gamut3')

        # Testujemy dla S-Gamut3.Cine
        df_sgamut3_cine = generate_table(filepath, 'S-Gamut3.Cine')
        self.assertIsInstance(df_sgamut3_cine, pd.DataFrame)
        self.assertEqual(len(df_sgamut3_cine), 20)
        self.assertEqual(df_sgamut3_cine['Color Space'][0], 'S-Gamut3.Cine')

        os.remove(filepath) # Usuwamy tymczasowy plik

    def test_logc4_curve(self):
      self.assertTrue(np.allclose(logc4_curve(0.0), np.array([-3852.359026659536])))
      self.assertAlmostEqual(logc4_curve(0.18), 0.4090068696819821)
      self.assertTrue(np.allclose(logc4_curve(np.array([0.0, 0.18, 1.0])), np.array([-3852.359026659536, 0.4090068696819821, 0.6577136499999999])))

    def test_inverse_logc4_curve(self):
      self.assertTrue(np.allclose(inverse_logc4_curve(0.09285527796717754), np.array([0.04345044])))
      self.assertTrue(np.allclose(inverse_logc4_curve(0.4090068696819821), np.array([0.18])))
      self.assertTrue(np.allclose(inverse_logc4_curve(np.array([0.09285527796717754, 0.4090068696819821, 0.6577136499999999])), np.array([0.04345044, 0.18, 1.0])))


if __name__ == '__main__':
    unittest.main()
</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.<environment_details>
# VSCode Visible Files
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
pixelpasta/tests/test_color_analysis.py

# VSCode Open Tabs
pixelpasta/tests/test_cube_parser.py
pixelpasta/lut_processor/cube_parser.py
pixelpasta/app.py
pixelpasta/lut_processor/color_analysis.py
pixelpasta/templates/upload.html
pixelpasta/tests/test_color_analysis.py

# Current Time
19/03/2025, 6:47:05 pm (Europe/Warsaw, UTC+1:00)

# Current Mode
ACT MODE
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])))

    def test_inverse_slog3_curve(self):
        a = 0.432699
        b = 0.009468
        c = 0.655
        d = 0.037584
        e = 0.01
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), np.array([0.1])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), np.array([1.0])))
        self.assertTrue(np.allclose(inverse_slog3_curve(np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])), np.array([ (0.01 - e) / d, 0.1, 1.0])))

    def test_rec709_oetf(self):
        self.assertAlmostEqual(rec709_oetf(0.0), 0.0)
        self.assertAlmostEqual(rec709_oetf(0.018), 0.08124794403514046)
        self.assertAlmostEqual(rec709_oetf(1.0), 1.0)
        self.assertTrue(np.allclose(rec709_oetf(np.array([0.0, 0.018, 1.0])), np.array([0.0, 0.08124794403514046, 1.0])))

    def test_interpolate_1d_lut(self):
        lut_1d = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]])
        output = interpolate_1d_lut(lut_1d, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_interpolate_3d_lut(self):
        lut_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]
        ])
        lut_size = 2
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([
            [0.  , 0.  , 0.  ],
            [0.5 , 0.5 , 0.5 ],
            [1.  , 1.  , 1.  ]
        ])
        output = interpolate_3d_lut(lut_3d, lut_size, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_srgb_to_rec709(self):
        rgb_values = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        expected_output_sgamut3 = np.array([
            [ 1.641 , -0.6636,  0.0117],
            [-0.3245,  1.6157, -0.0085],
            [-0.3165,  0.0479,  0.9968]
        ])
        expected_output_sgamut3_cine = np.array([
            [ 1.5529, -0.5428, -0.0026],
            [-0.2555,  1.5027, -0.0186],
            [-0.2974,  0.0401,  1.0212]
        ])
        output_sgamut3 = srgb_to_rec709(rgb_values, 'S-Gamut3')
        output_sgamut3_cine = srgb_to_rec709(rgb_values, 'S-Gamut3.Cine')
        self.assertTrue(np.allclose(output_sgamut3, expected_output_sgamut3))
        self.assertTrue(np.allclose(output_sgamut3_cine, expected_output_sgamut3_cine))
        with self.assertRaises(ValueError):
            srgb_to_rec709(rgb_values, 'InvalidColorSpace')

    def test_generate_table(self):
        # Tworzymy tymczasowy plik .cube
        content = """
TITLE "Test LUT"
LUT_1D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as temp_file:
            temp_file.write(content.encode())
            filepath = temp_file.name

        # Testujemy dla S-Gamut3
        df_sgamut3 = generate_table(filepath, 'S-Gamut3')
        self.assertIsInstance(df_sgamut3, pd.DataFrame)
        self.assertEqual(len(df_sgamut3), 20)
        self.assertEqual(df_sgamut3['Color Space'][0], 'S-Gamut3')

        # Testujemy dla S-Gamut3.Cine
        df_sgamut3_cine = generate_table(filepath, 'S-Gamut3.Cine')
        self.assertIsInstance(df_sgamut3_cine, pd.DataFrame)
        self.assertEqual(len(df_sgamut3_cine), 20)
        self.assertEqual(df_sgamut3_cine['Color Space'][0], 'S-Gamut3.Cine')

        os.remove(filepath) # Usuwamy tymczasowy plik

    def test_logc4_curve(self):
      self.assertTrue(np.allclose(logc4_curve(0.0), np.array([-3852.359026659536])))
      self.assertAlmostEqual(logc4_curve(0.18), 0.4090068696819821)
      self.assertTrue(np.allclose(logc4_curve(np.array([0.0, 0.18, 1.0])), np.array([-3852.359026659536, 0.4090068696819821, 0.6577136499999999])))

    def test_inverse_logc4_curve(self):
      self.assertTrue(np.allclose(inverse_logc4_curve(0.09285527796717754), np.array([0.04345044])))
      self.assertTrue(np.allclose(inverse_logc4_curve(0.4090068696819821), np.array([0.18])))
      self.assertTrue(np.allclose(inverse_logc4_curve(np.array([0.09285527796717754, 0.4090068696819821, 0.6577136499999999])), np.array([0.04345044, 0.18, 1.0])))


if __name__ == '__main__':
    unittest.main()
</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.<environment_details>
# VSCode Visible Files
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
pixelpasta/tests/test_color_analysis.py

# VSCode Open Tabs
pixelpasta/tests/test_cube_parser.py
pixelpasta/lut_processor/cube_parser.py
pixelpasta/app.py
pixelpasta/lut_processor/color_analysis.py
pixelpasta/templates/upload.html
pixelpasta/tests/test_color_analysis.py

# Current Time
19/03/2025, 6:47:05 pm (Europe/Warsaw, UTC+1:00)

# Current Mode
ACT MODE
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])))

    def test_inverse_slog3_curve(self):
        a = 0.432699
        b = 0.009468
        c = 0.655
        d = 0.037584
        e = 0.01
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), np.array([0.1])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), np.array([1.0])))
        self.assertTrue(np.allclose(inverse_slog3_curve(np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])), np.array([ (0.01 - e) / d, 0.1, 1.0])))

    def test_rec709_oetf(self):
        self.assertAlmostEqual(rec709_oetf(0.0), 0.0)
        self.assertAlmostEqual(rec709_oetf(0.018), 0.08124794403514046)
        self.assertAlmostEqual(rec709_oetf(1.0), 1.0)
        self.assertTrue(np.allclose(rec709_oetf(np.array([0.0, 0.018, 1.0])), np.array([0.0, 0.08124794403514046, 1.0])))

    def test_interpolate_1d_lut(self):
        lut_1d = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]])
        output = interpolate_1d_lut(lut_1d, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_interpolate_3d_lut(self):
        lut_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]
        ])
        lut_size = 2
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([
            [0.  , 0.  , 0.  ],
            [0.5 , 0.5 , 0.5 ],
            [1.  , 1.  , 1.  ]
        ])
        output = interpolate_3d_lut(lut_3d, lut_size, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_srgb_to_rec709(self):
        rgb_values = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        expected_output_sgamut3 = np.array([
            [ 1.641 , -0.6636,  0.0117],
            [-0.3245,  1.6157, -0.0085],
            [-0.3165,  0.0479,  0.9968]
        ])
        expected_output_sgamut3_cine = np.array([
            [ 1.5529, -0.5428, -0.0026],
            [-0.2555,  1.5027, -0.0186],
            [-0.2974,  0.0401,  1.0212]
        ])
        output_sgamut3 = srgb_to_rec709(rgb_values, 'S-Gamut3')
        output_sgamut3_cine = srgb_to_rec709(rgb_values, 'S-Gamut3.Cine')
        self.assertTrue(np.allclose(output_sgamut3, expected_output_sgamut3))
        self.assertTrue(np.allclose(output_sgamut3_cine, expected_output_sgamut3_cine))
        with self.assertRaises(ValueError):
            srgb_to_rec709(rgb_values, 'InvalidColorSpace')

    def test_generate_table(self):
        # Tworzymy tymczasowy plik .cube
        content = """
TITLE "Test LUT"
LUT_1D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as temp_file:
            temp_file.write(content.encode())
            filepath = temp_file.name

        # Testujemy dla S-Gamut3
        df_sgamut3 = generate_table(filepath, 'S-Gamut3')
        self.assertIsInstance(df_sgamut3, pd.DataFrame)
        self.assertEqual(len(df_sgamut3), 20)
        self.assertEqual(df_sgamut3['Color Space'][0], 'S-Gamut3')

        # Testujemy dla S-Gamut3.Cine
        df_sgamut3_cine = generate_table(filepath, 'S-Gamut3.Cine')
        self.assertIsInstance(df_sgamut3_cine, pd.DataFrame)
        self.assertEqual(len(df_sgamut3_cine), 20)
        self.assertEqual(df_sgamut3_cine['Color Space'][0], 'S-Gamut3.Cine')

        os.remove(filepath) # Usuwamy tymczasowy plik

    def test_logc4_curve(self):
      self.assertTrue(np.allclose(logc4_curve(0.0), np.array([-3852.359026659536])))
      self.assertAlmostEqual(logc4_curve(0.18), 0.4090068696819821)
      self.assertTrue(np.allclose(logc4_curve(np.array([0.0, 0.18, 1.0])), np.array([-3852.359026659536, 0.4090068696819821, 0.6577136499999999])))

    def test_inverse_logc4_curve(self):
      self.assertTrue(np.allclose(inverse_logc4_curve(0.09285527796717754), np.array([0.04345044])))
      self.assertTrue(np.allclose(inverse_logc4_curve(0.4090068696819821), np.array([0.18])))
      self.assertTrue(np.allclose(inverse_logc4_curve(np.array([0.09285527796717754, 0.4090068696819821, 0.6577136499999999])), np.array([0.04345044, 0.18, 1.0])))


if __name__ == '__main__':
    unittest.main()
</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.<environment_details>
# VSCode Visible Files
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
pixelpasta/tests/test_color_analysis.py

# VSCode Open Tabs
pixelpasta/tests/test_cube_parser.py
pixelpasta/lut_processor/cube_parser.py
pixelpasta/app.py
pixelpasta/lut_processor/color_analysis.py
pixelpasta/templates/upload.html
pixelpasta/tests/test_color_analysis.py

# Current Time
19/03/2025, 6:47:05 pm (Europe/Warsaw, UTC+1:00)

# Current Mode
ACT MODE
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])))

    def test_inverse_slog3_curve(self):
        a = 0.432699
        b = 0.009468
        c = 0.655
        d = 0.037584
        e = 0.01
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), np.array([0.1])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), np.array([1.0])))
        self.assertTrue(np.allclose(inverse_slog3_curve(np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])), np.array([ (0.01 - e) / d, 0.1, 1.0])))

    def test_rec709_oetf(self):
        self.assertAlmostEqual(rec709_oetf(0.0), 0.0)
        self.assertAlmostEqual(rec709_oetf(0.018), 0.08124794403514046)
        self.assertAlmostEqual(rec709_oetf(1.0), 1.0)
        self.assertTrue(np.allclose(rec709_oetf(np.array([0.0, 0.018, 1.0])), np.array([0.0, 0.08124794403514046, 1.0])))

    def test_interpolate_1d_lut(self):
        lut_1d = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]])
        output = interpolate_1d_lut(lut_1d, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_interpolate_3d_lut(self):
        lut_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]
        ])
        lut_size = 2
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([
            [0.  , 0.  , 0.  ],
            [0.5 , 0.5 , 0.5 ],
            [1.  , 1.  , 1.  ]
        ])
        output = interpolate_3d_lut(lut_3d, lut_size, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_srgb_to_rec709(self):
        rgb_values = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        expected_output_sgamut3 = np.array([
            [ 1.641 , -0.6636,  0.0117],
            [-0.3245,  1.6157, -0.0085],
            [-0.3165,  0.0479,  0.9968]
        ])
        expected_output_sgamut3_cine = np.array([
            [ 1.5529, -0.5428, -0.0026],
            [-0.2555,  1.5027, -0.0186],
            [-0.2974,  0.0401,  1.0212]
        ])
        output_sgamut3 = srgb_to_rec709(rgb_values, 'S-Gamut3')
        output_sgamut3_cine = srgb_to_rec709(rgb_values, 'S-Gamut3.Cine')
        self.assertTrue(np.allclose(output_sgamut3, expected_output_sgamut3))
        self.assertTrue(np.allclose(output_sgamut3_cine, expected_output_sgamut3_cine))
        with self.assertRaises(ValueError):
            srgb_to_rec709(rgb_values, 'InvalidColorSpace')

    def test_generate_table(self):
        # Tworzymy tymczasowy plik .cube
        content = """
TITLE "Test LUT"
LUT_1D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as temp_file:
            temp_file.write(content.encode())
            filepath = temp_file.name

        # Testujemy dla S-Gamut3
        df_sgamut3 = generate_table(filepath, 'S-Gamut3')
        self.assertIsInstance(df_sgamut3, pd.DataFrame)
        self.assertEqual(len(df_sgamut3), 20)
        self.assertEqual(df_sgamut3['Color Space'][0], 'S-Gamut3')

        # Testujemy dla S-Gamut3.Cine
        df_sgamut3_cine = generate_table(filepath, 'S-Gamut3.Cine')
        self.assertIsInstance(df_sgamut3_cine, pd.DataFrame)
        self.assertEqual(len(df_sgamut3_cine), 20)
        self.assertEqual(df_sgamut3_cine['Color Space'][0], 'S-Gamut3.Cine')

        os.remove(filepath) # Usuwamy tymczasowy plik

    def test_logc4_curve(self):
      self.assertTrue(np.allclose(logc4_curve(0.0), np.array([-3852.359026659536])))
      self.assertAlmostEqual(logc4_curve(0.18), 0.4090068696819821)
      self.assertTrue(np.allclose(logc4_curve(np.array([0.0, 0.18, 1.0])), np.array([-3852.359026659536, 0.4090068696819821, 0.6577136499999999])))

    def test_inverse_logc4_curve(self):
      self.assertTrue(np.allclose(inverse_logc4_curve(0.09285527796717754), np.array([0.04345044])))
      self.assertTrue(np.allclose(inverse_logc4_curve(0.4090068696819821), np.array([0.18])))
      self.assertTrue(np.allclose(inverse_logc4_curve(np.array([0.09285527796717754, 0.4090068696819821, 0.6577136499999999])), np.array([0.04345044, 0.18, 1.0])))


if __name__ == '__main__':
    unittest.main()
</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.<environment_details>
# VSCode Visible Files
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
pixelpasta/tests/test_color_analysis.py

# VSCode Open Tabs
pixelpasta/tests/test_cube_parser.py
pixelpasta/lut_processor/cube_parser.py
pixelpasta/app.py
pixelpasta/lut_processor/color_analysis.py
pixelpasta/templates/upload.html
pixelpasta/tests/test_color_analysis.py

# Current Time
19/03/2025, 6:47:05 pm (Europe/Warsaw, UTC+1:00)

# Current Mode
ACT MODE
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])))

    def test_inverse_slog3_curve(self):
        a = 0.432699
        b = 0.009468
        c = 0.655
        d = 0.037584
        e = 0.01
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), np.array([0.1])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), np.array([1.0])))
        self.assertTrue(np.allclose(inverse_slog3_curve(np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])), np.array([ (0.01 - e) / d, 0.1, 1.0])))

    def test_rec709_oetf(self):
        self.assertAlmostEqual(rec709_oetf(0.0), 0.0)
        self.assertAlmostEqual(rec709_oetf(0.018), 0.08124794403514046)
        self.assertAlmostEqual(rec709_oetf(1.0), 1.0)
        self.assertTrue(np.allclose(rec709_oetf(np.array([0.0, 0.018, 1.0])), np.array([0.0, 0.08124794403514046, 1.0])))

    def test_interpolate_1d_lut(self):
        lut_1d = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]])
        output = interpolate_1d_lut(lut_1d, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_interpolate_3d_lut(self):
        lut_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]
        ])
        lut_size = 2
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([
            [0.  , 0.  , 0.  ],
            [0.5 , 0.5 , 0.5 ],
            [1.  , 1.  , 1.  ]
        ])
        output = interpolate_3d_lut(lut_3d, lut_size, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_srgb_to_rec709(self):
        rgb_values = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        expected_output_sgamut3 = np.array([
            [ 1.641 , -0.6636,  0.0117],
            [-0.3245,  1.6157, -0.0085],
            [-0.3165,  0.0479,  0.9968]
        ])
        expected_output_sgamut3_cine = np.array([
            [ 1.5529, -0.5428, -0.0026],
            [-0.2555,  1.5027, -0.0186],
            [-0.2974,  0.0401,  1.0212]
        ])
        output_sgamut3 = srgb_to_rec709(rgb_values, 'S-Gamut3')
        output_sgamut3_cine = srgb_to_rec709(rgb_values, 'S-Gamut3.Cine')
        self.assertTrue(np.allclose(output_sgamut3, expected_output_sgamut3))
        self.assertTrue(np.allclose(output_sgamut3_cine, expected_output_sgamut3_cine))
        with self.assertRaises(ValueError):
            srgb_to_rec709(rgb_values, 'InvalidColorSpace')

    def test_generate_table(self):
        # Tworzymy tymczasowy plik .cube
        content = """
TITLE "Test LUT"
LUT_1D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as temp_file:
            temp_file.write(content.encode())
            filepath = temp_file.name

        # Testujemy dla S-Gamut3
        df_sgamut3 = generate_table(filepath, 'S-Gamut3')
        self.assertIsInstance(df_sgamut3, pd.DataFrame)
        self.assertEqual(len(df_sgamut3), 20)
        self.assertEqual(df_sgamut3['Color Space'][0], 'S-Gamut3')

        # Testujemy dla S-Gamut3.Cine
        df_sgamut3_cine = generate_table(filepath, 'S-Gamut3.Cine')
        self.assertIsInstance(df_sgamut3_cine, pd.DataFrame)
        self.assertEqual(len(df_sgamut3_cine), 20)
        self.assertEqual(df_sgamut3_cine['Color Space'][0], 'S-Gamut3.Cine')

        os.remove(filepath) # Usuwamy tymczasowy plik

    def test_logc4_curve(self):
      self.assertTrue(np.allclose(logc4_curve(0.0), np.array([-3852.359026659536])))
      self.assertAlmostEqual(logc4_curve(0.18), 0.4090068696819821)
      self.assertTrue(np.allclose(logc4_curve(np.array([0.0, 0.18, 1.0])), np.array([-3852.359026659536, 0.4090068696819821, 0.6577136499999999])))

    def test_inverse_logc4_curve(self):
      self.assertTrue(np.allclose(inverse_logc4_curve(0.09285527796717754), np.array([0.04345044])))
      self.assertTrue(np.allclose(inverse_logc4_curve(0.4090068696819821), np.array([0.18])))
      self.assertTrue(np.allclose(inverse_logc4_curve(np.array([0.09285527796717754, 0.4090068696819821, 0.6577136499999999])), np.array([0.04345044, 0.18, 1.0])))


if __name__ == '__main__':
    unittest.main()
</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.<environment_details>
# VSCode Visible Files
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
pixelpasta/tests/test_color_analysis.py

# VSCode Open Tabs
pixelpasta/tests/test_cube_parser.py
pixelpasta/lut_processor/cube_parser.py
pixelpasta/app.py
pixelpasta/lut_processor/color_analysis.py
pixelpasta/templates/upload.html
pixelpasta/tests/test_color_analysis.py

# Current Time
19/03/2025, 6:47:05 pm (Europe/Warsaw, UTC+1:00)

# Current Mode
ACT MODE
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])))

    def test_inverse_slog3_curve(self):
        a = 0.432699
        b = 0.009468
        c = 0.655
        d = 0.037584
        e = 0.01
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), np.array([0.1])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), np.array([1.0])))
        self.assertTrue(np.allclose(inverse_slog3_curve(np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])), np.array([ (0.01 - e) / d, 0.1, 1.0])))

    def test_rec709_oetf(self):
        self.assertAlmostEqual(rec709_oetf(0.0), 0.0)
        self.assertAlmostEqual(rec709_oetf(0.018), 0.08124794403514046)
        self.assertAlmostEqual(rec709_oetf(1.0), 1.0)
        self.assertTrue(np.allclose(rec709_oetf(np.array([0.0, 0.018, 1.0])), np.array([0.0, 0.08124794403514046, 1.0])))

    def test_interpolate_1d_lut(self):
        lut_1d = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]])
        output = interpolate_1d_lut(lut_1d, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_interpolate_3d_lut(self):
        lut_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]
        ])
        lut_size = 2
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([
            [0.  , 0.  , 0.  ],
            [0.5 , 0.5 , 0.5 ],
            [1.  , 1.  , 1.  ]
        ])
        output = interpolate_3d_lut(lut_3d, lut_size, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_srgb_to_rec709(self):
        rgb_values = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        expected_output_sgamut3 = np.array([
            [ 1.641 , -0.6636,  0.0117],
            [-0.3245,  1.6157, -0.0085],
            [-0.3165,  0.0479,  0.9968]
        ])
        expected_output_sgamut3_cine = np.array([
            [ 1.5529, -0.5428, -0.0026],
            [-0.2555,  1.5027, -0.0186],
            [-0.2974,  0.0401,  1.0212]
        ])
        output_sgamut3 = srgb_to_rec709(rgb_values, 'S-Gamut3')
        output_sgamut3_cine = srgb_to_rec709(rgb_values, 'S-Gamut3.Cine')
        self.assertTrue(np.allclose(output_sgamut3, expected_output_sgamut3))
        self.assertTrue(np.allclose(output_sgamut3_cine, expected_output_sgamut3_cine))
        with self.assertRaises(ValueError):
            srgb_to_rec709(rgb_values, 'InvalidColorSpace')

    def test_generate_table(self):
        # Tworzymy tymczasowy plik .cube
        content = """
TITLE "Test LUT"
LUT_1D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as temp_file:
            temp_file.write(content.encode())
            filepath = temp_file.name

        # Testujemy dla S-Gamut3
        df_sgamut3 = generate_table(filepath, 'S-Gamut3')
        self.assertIsInstance(df_sgamut3, pd.DataFrame)
        self.assertEqual(len(df_sgamut3), 20)
        self.assertEqual(df_sgamut3['Color Space'][0], 'S-Gamut3')

        # Testujemy dla S-Gamut3.Cine
        df_sgamut3_cine = generate_table(filepath, 'S-Gamut3.Cine')
        self.assertIsInstance(df_sgamut3_cine, pd.DataFrame)
        self.assertEqual(len(df_sgamut3_cine), 20)
        self.assertEqual(df_sgamut3_cine['Color Space'][0], 'S-Gamut3.Cine')

        os.remove(filepath) # Usuwamy tymczasowy plik

    def test_logc4_curve(self):
      self.assertTrue(np.allclose(logc4_curve(0.0), np.array([-3852.359026659536])))
      self.assertAlmostEqual(logc4_curve(0.18), 0.4090068696819821)
      self.assertTrue(np.allclose(logc4_curve(np.array([0.0, 0.18, 1.0])), np.array([-3852.359026659536, 0.4090068696819821, 0.6577136499999999])))

    def test_inverse_logc4_curve(self):
      self.assertTrue(np.allclose(inverse_logc4_curve(0.09285527796717754), np.array([0.04345044])))
      self.assertTrue(np.allclose(inverse_logc4_curve(0.4090068696819821), np.array([0.18])))
      self.assertTrue(np.allclose(inverse_logc4_curve(np.array([0.09285527796717754, 0.4090068696819821, 0.6577136499999999])), np.array([0.04345044, 0.18, 1.0])))


if __name__ == '__main__':
    unittest.main()
</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.<environment_details>
# VSCode Visible Files
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
pixelpasta/tests/test_color_analysis.py

# VSCode Open Tabs
pixelpasta/tests/test_cube_parser.py
pixelpasta/lut_processor/cube_parser.py
pixelpasta/app.py
pixelpasta/lut_processor/color_analysis.py
pixelpasta/templates/upload.html
pixelpasta/tests/test_color_analysis.py

# Current Time
19/03/2025, 6:47:05 pm (Europe/Warsaw, UTC+1:00)

# Current Mode
ACT MODE
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])))

    def test_inverse_slog3_curve(self):
        a = 0.432699
        b = 0.009468
        c = 0.655
        d = 0.037584
        e = 0.01
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), np.array([0.1])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), np.array([1.0])))
        self.assertTrue(np.allclose(inverse_slog3_curve(np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])), np.array([ (0.01 - e) / d, 0.1, 1.0])))

    def test_rec709_oetf(self):
        self.assertAlmostEqual(rec709_oetf(0.0), 0.0)
        self.assertAlmostEqual(rec709_oetf(0.018), 0.08124794403514046)
        self.assertAlmostEqual(rec709_oetf(1.0), 1.0)
        self.assertTrue(np.allclose(rec709_oetf(np.array([0.0, 0.018, 1.0])), np.array([0.0, 0.08124794403514046, 1.0])))

    def test_interpolate_1d_lut(self):
        lut_1d = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]])
        output = interpolate_1d_lut(lut_1d, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_interpolate_3d_lut(self):
        lut_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]
        ])
        lut_size = 2
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([
            [0.  , 0.  , 0.  ],
            [0.5 , 0.5 , 0.5 ],
            [1.  , 1.  , 1.  ]
        ])
        output = interpolate_3d_lut(lut_3d, lut_size, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_srgb_to_rec709(self):
        rgb_values = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        expected_output_sgamut3 = np.array([
            [ 1.641 , -0.6636,  0.0117],
            [-0.3245,  1.6157, -0.0085],
            [-0.3165,  0.0479,  0.9968]
        ])
        expected_output_sgamut3_cine = np.array([
            [ 1.5529, -0.5428, -0.0026],
            [-0.2555,  1.5027, -0.0186],
            [-0.2974,  0.0401,  1.0212]
        ])
        output_sgamut3 = srgb_to_rec709(rgb_values, 'S-Gamut3')
        output_sgamut3_cine = srgb_to_rec709(rgb_values, 'S-Gamut3.Cine')
        self.assertTrue(np.allclose(output_sgamut3, expected_output_sgamut3))
        self.assertTrue(np.allclose(output_sgamut3_cine, expected_output_sgamut3_cine))
        with self.assertRaises(ValueError):
            srgb_to_rec709(rgb_values, 'InvalidColorSpace')

    def test_generate_table(self):
        # Tworzymy tymczasowy plik .cube
        content = """
TITLE "Test LUT"
LUT_1D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as temp_file:
            temp_file.write(content.encode())
            filepath = temp_file.name

        # Testujemy dla S-Gamut3
        df_sgamut3 = generate_table(filepath, 'S-Gamut3')
        self.assertIsInstance(df_sgamut3, pd.DataFrame)
        self.assertEqual(len(df_sgamut3), 20)
        self.assertEqual(df_sgamut3['Color Space'][0], 'S-Gamut3')

        # Testujemy dla S-Gamut3.Cine
        df_sgamut3_cine = generate_table(filepath, 'S-Gamut3.Cine')
        self.assertIsInstance(df_sgamut3_cine, pd.DataFrame)
        self.assertEqual(len(df_sgamut3_cine), 20)
        self.assertEqual(df_sgamut3_cine['Color Space'][0], 'S-Gamut3.Cine')

        os.remove(filepath) # Usuwamy tymczasowy plik

    def test_logc4_curve(self):
      self.assertTrue(np.allclose(logc4_curve(0.0), np.array([-3852.359026659536])))
      self.assertAlmostEqual(logc4_curve(0.18), 0.4090068696819821)
      self.assertTrue(np.allclose(logc4_curve(np.array([0.0, 0.18, 1.0])), np.array([-3852.359026659536, 0.4090068696819821, 0.6577136499999999])))

    def test_inverse_logc4_curve(self):
      self.assertTrue(np.allclose(inverse_logc4_curve(0.09285527796717754), np.array([0.04345044])))
      self.assertTrue(np.allclose(inverse_logc4_curve(0.4090068696819821), np.array([0.18])))
      self.assertTrue(np.allclose(inverse_logc4_curve(np.array([0.09285527796717754, 0.4090068696819821, 0.6577136499999999])), np.array([0.04345044, 0.18, 1.0])))


if __name__ == '__main__':
    unittest.main()
</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.<environment_details>
# VSCode Visible Files
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
pixelpasta/tests/test_color_analysis.py

# VSCode Open Tabs
pixelpasta/tests/test_cube_parser.py
pixelpasta/lut_processor/cube_parser.py
pixelpasta/app.py
pixelpasta/lut_processor/color_analysis.py
pixelpasta/templates/upload.html
pixelpasta/tests/test_color_analysis.py

# Current Time
19/03/2025, 6:47:05 pm (Europe/Warsaw, UTC+1:00)

# Current Mode
ACT MODE
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])))

    def test_inverse_slog3_curve(self):
        a = 0.432699
        b = 0.009468
        c = 0.655
        d = 0.037584
        e = 0.01
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), np.array([0.1])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), np.array([1.0])))
        self.assertTrue(np.allclose(inverse_slog3_curve(np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])), np.array([ (0.01 - e) / d, 0.1, 1.0])))

    def test_rec709_oetf(self):
        self.assertAlmostEqual(rec709_oetf(0.0), 0.0)
        self.assertAlmostEqual(rec709_oetf(0.018), 0.08124794403514046)
        self.assertAlmostEqual(rec709_oetf(1.0), 1.0)
        self.assertTrue(np.allclose(rec709_oetf(np.array([0.0, 0.018, 1.0])), np.array([0.0, 0.08124794403514046, 1.0])))

    def test_interpolate_1d_lut(self):
        lut_1d = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]])
        output = interpolate_1d_lut(lut_1d, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_interpolate_3d_lut(self):
        lut_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]
        ])
        lut_size = 2
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([
            [0.  , 0.  , 0.  ],
            [0.5 , 0.5 , 0.5 ],
            [1.  , 1.  , 1.  ]
        ])
        output = interpolate_3d_lut(lut_3d, lut_size, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_srgb_to_rec709(self):
        rgb_values = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        expected_output_sgamut3 = np.array([
            [ 1.641 , -0.6636,  0.0117],
            [-0.3245,  1.6157, -0.0085],
            [-0.3165,  0.0479,  0.9968]
        ])
        expected_output_sgamut3_cine = np.array([
            [ 1.5529, -0.5428, -0.0026],
            [-0.2555,  1.5027, -0.0186],
            [-0.2974,  0.0401,  1.0212]
        ])
        output_sgamut3 = srgb_to_rec709(rgb_values, 'S-Gamut3')
        output_sgamut3_cine = srgb_to_rec709(rgb_values, 'S-Gamut3.Cine')
        self.assertTrue(np.allclose(output_sgamut3, expected_output_sgamut3))
        self.assertTrue(np.allclose(output_sgamut3_cine, expected_output_sgamut3_cine))
        with self.assertRaises(ValueError):
            srgb_to_rec709(rgb_values, 'InvalidColorSpace')

    def test_generate_table(self):
        # Tworzymy tymczasowy plik .cube
        content = """
TITLE "Test LUT"
LUT_1D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as temp_file:
            temp_file.write(content.encode())
            filepath = temp_file.name

        # Testujemy dla S-Gamut3
        df_sgamut3 = generate_table(filepath, 'S-Gamut3')
        self.assertIsInstance(df_sgamut3, pd.DataFrame)
        self.assertEqual(len(df_sgamut3), 20)
        self.assertEqual(df_sgamut3['Color Space'][0], 'S-Gamut3')

        # Testujemy dla S-Gamut3.Cine
        df_sgamut3_cine = generate_table(filepath, 'S-Gamut3.Cine')
        self.assertIsInstance(df_sgamut3_cine, pd.DataFrame)
        self.assertEqual(len(df_sgamut3_cine), 20)
        self.assertEqual(df_sgamut3_cine['Color Space'][0], 'S-Gamut3.Cine')

        os.remove(filepath) # Usuwamy tymczasowy plik

    def test_logc4_curve(self):
      self.assertTrue(np.allclose(logc4_curve(0.0), np.array([-3852.359026659536])))
      self.assertAlmostEqual(logc4_curve(0.18), 0.4090068696819821)
      self.assertTrue(np.allclose(logc4_curve(np.array([0.0, 0.18, 1.0])), np.array([-3852.359026659536, 0.4090068696819821, 0.6577136499999999])))

    def test_inverse_logc4_curve(self):
      self.assertTrue(np.allclose(inverse_logc4_curve(0.09285527796717754), np.array([0.04345044])))
      self.assertTrue(np.allclose(inverse_logc4_curve(0.4090068696819821), np.array([0.18])))
      self.assertTrue(np.allclose(inverse_logc4_curve(np.array([0.09285527796717754, 0.4090068696819821, 0.6577136499999999])), np.array([0.04345044, 0.18, 1.0])))


if __name__ == '__main__':
    unittest.main()
</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.<environment_details>
# VSCode Visible Files
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
pixelpasta/tests/test_color_analysis.py

# VSCode Open Tabs
pixelpasta/tests/test_cube_parser.py
pixelpasta/lut_processor/cube_parser.py
pixelpasta/app.py
pixelpasta/lut_processor/color_analysis.py
pixelpasta/templates/upload.html
pixelpasta/tests/test_color_analysis.py

# Current Time
19/03/2025, 6:47:05 pm (Europe/Warsaw, UTC+1:00)

# Current Mode
ACT MODE
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])))

    def test_inverse_slog3_curve(self):
        a = 0.432699
        b = 0.009468
        c = 0.655
        d = 0.037584
        e = 0.01
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), np.array([0.1])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), np.array([1.0])))
        self.assertTrue(np.allclose(inverse_slog3_curve(np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])), np.array([ (0.01 - e) / d, 0.1, 1.0])))

    def test_rec709_oetf(self):
        self.assertAlmostEqual(rec709_oetf(0.0), 0.0)
        self.assertAlmostEqual(rec709_oetf(0.018), 0.08124794403514046)
        self.assertAlmostEqual(rec709_oetf(1.0), 1.0)
        self.assertTrue(np.allclose(rec709_oetf(np.array([0.0, 0.018, 1.0])), np.array([0.0, 0.08124794403514046, 1.0])))

    def test_interpolate_1d_lut(self):
        lut_1d = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]])
        output = interpolate_1d_lut(lut_1d, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_interpolate_3d_lut(self):
        lut_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]
        ])
        lut_size = 2
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([
            [0.  , 0.  , 0.  ],
            [0.5 , 0.5 , 0.5 ],
            [1.  , 1.  , 1.  ]
        ])
        output = interpolate_3d_lut(lut_3d, lut_size, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_srgb_to_rec709(self):
        rgb_values = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        expected_output_sgamut3 = np.array([
            [ 1.641 , -0.6636,  0.0117],
            [-0.3245,  1.6157, -0.0085],
            [-0.3165,  0.0479,  0.9968]
        ])
        expected_output_sgamut3_cine = np.array([
            [ 1.5529, -0.5428, -0.0026],
            [-0.2555,  1.5027, -0.0186],
            [-0.2974,  0.0401,  1.0212]
        ])
        output_sgamut3 = srgb_to_rec709(rgb_values, 'S-Gamut3')
        output_sgamut3_cine = srgb_to_rec709(rgb_values, 'S-Gamut3.Cine')
        self.assertTrue(np.allclose(output_sgamut3, expected_output_sgamut3))
        self.assertTrue(np.allclose(output_sgamut3_cine, expected_output_sgamut3_cine))
        with self.assertRaises(ValueError):
            srgb_to_rec709(rgb_values, 'InvalidColorSpace')

    def test_generate_table(self):
        # Tworzymy tymczasowy plik .cube
        content = """
TITLE "Test LUT"
LUT_1D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as temp_file:
            temp_file.write(content.encode())
            filepath = temp_file.name

        # Testujemy dla S-Gamut3
        df_sgamut3 = generate_table(filepath, 'S-Gamut3')
        self.assertIsInstance(df_sgamut3, pd.DataFrame)
        self.assertEqual(len(df_sgamut3), 20)
        self.assertEqual(df_sgamut3['Color Space'][0], 'S-Gamut3')

        # Testujemy dla S-Gamut3.Cine
        df_sgamut3_cine = generate_table(filepath, 'S-Gamut3.Cine')
        self.assertIsInstance(df_sgamut3_cine, pd.DataFrame)
        self.assertEqual(len(df_sgamut3_cine), 20)
        self.assertEqual(df_sgamut3_cine['Color Space'][0], 'S-Gamut3.Cine')

        os.remove(filepath) # Usuwamy tymczasowy plik

    def test_logc4_curve(self):
      self.assertTrue(np.allclose(logc4_curve(0.0), np.array([-3852.359026659536])))
      self.assertAlmostEqual(logc4_curve(0.18), 0.4090068696819821)
      self.assertTrue(np.allclose(logc4_curve(np.array([0.0, 0.18, 1.0])), np.array([-3852.359026659536, 0.4090068696819821, 0.6577136499999999])))

    def test_inverse_logc4_curve(self):
      self.assertTrue(np.allclose(inverse_logc4_curve(0.09285527796717754), np.array([0.04345044])))
      self.assertTrue(np.allclose(inverse_logc4_curve(0.4090068696819821), np.array([0.18])))
      self.assertTrue(np.allclose(inverse_logc4_curve(np.array([0.09285527796717754, 0.4090068696819821, 0.6577136499999999])), np.array([0.04345044, 0.18, 1.0])))


if __name__ == '__main__':
    unittest.main()
</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.<environment_details>
# VSCode Visible Files
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
pixelpasta/tests/test_color_analysis.py

# VSCode Open Tabs
pixelpasta/tests/test_cube_parser.py
pixelpasta/lut_processor/cube_parser.py
pixelpasta/app.py
pixelpasta/lut_processor/color_analysis.py
pixelpasta/templates/upload.html
pixelpasta/tests/test_color_analysis.py

# Current Time
19/03/2025, 6:47:05 pm (Europe/Warsaw, UTC+1:00)

# Current Mode
ACT MODE
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])))

    def test_inverse_slog3_curve(self):
        a = 0.432699
        b = 0.009468
        c = 0.655
        d = 0.037584
        e = 0.01
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), np.array([0.1])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), np.array([1.0])))
        self.assertTrue(np.allclose(inverse_slog3_curve(np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])), np.array([ (0.01 - e) / d, 0.1, 1.0])))

    def test_rec709_oetf(self):
        self.assertAlmostEqual(rec709_oetf(0.0), 0.0)
        self.assertAlmostEqual(rec709_oetf(0.018), 0.08124794403514046)
        self.assertAlmostEqual(rec709_oetf(1.0), 1.0)
        self.assertTrue(np.allclose(rec709_oetf(np.array([0.0, 0.018, 1.0])), np.array([0.0, 0.08124794403514046, 1.0])))

    def test_interpolate_1d_lut(self):
        lut_1d = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]])
        output = interpolate_1d_lut(lut_1d, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_interpolate_3d_lut(self):
        lut_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]
        ])
        lut_size = 2
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([
            [0.  , 0.  , 0.  ],
            [0.5 , 0.5 , 0.5 ],
            [1.  , 1.  , 1.  ]
        ])
        output = interpolate_3d_lut(lut_3d, lut_size, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_srgb_to_rec709(self):
        rgb_values = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        expected_output_sgamut3 = np.array([
            [ 1.641 , -0.6636,  0.0117],
            [-0.3245,  1.6157, -0.0085],
            [-0.3165,  0.0479,  0.9968]
        ])
        expected_output_sgamut3_cine = np.array([
            [ 1.5529, -0.5428, -0.0026],
            [-0.2555,  1.5027, -0.0186],
            [-0.2974,  0.0401,  1.0212]
        ])
        output_sgamut3 = srgb_to_rec709(rgb_values, 'S-Gamut3')
        output_sgamut3_cine = srgb_to_rec709(rgb_values, 'S-Gamut3.Cine')
        self.assertTrue(np.allclose(output_sgamut3, expected_output_sgamut3))
        self.assertTrue(np.allclose(output_sgamut3_cine, expected_output_sgamut3_cine))
        with self.assertRaises(ValueError):
            srgb_to_rec709(rgb_values, 'InvalidColorSpace')

    def test_generate_table(self):
        # Tworzymy tymczasowy plik .cube
        content = """
TITLE "Test LUT"
LUT_1D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as temp_file:
            temp_file.write(content.encode())
            filepath = temp_file.name

        # Testujemy dla S-Gamut3
        df_sgamut3 = generate_table(filepath, 'S-Gamut3')
        self.assertIsInstance(df_sgamut3, pd.DataFrame)
        self.assertEqual(len(df_sgamut3), 20)
        self.assertEqual(df_sgamut3['Color Space'][0], 'S-Gamut3')

        # Testujemy dla S-Gamut3.Cine
        df_sgamut3_cine = generate_table(filepath, 'S-Gamut3.Cine')
        self.assertIsInstance(df_sgamut3_cine, pd.DataFrame)
        self.assertEqual(len(df_sgamut3_cine), 20)
        self.assertEqual(df_sgamut3_cine['Color Space'][0], 'S-Gamut3.Cine')

        os.remove(filepath) # Usuwamy tymczasowy plik

    def test_logc4_curve(self):
      self.assertTrue(np.allclose(logc4_curve(0.0), np.array([-3852.359026659536])))
      self.assertAlmostEqual(logc4_curve(0.18), 0.4090068696819821)
      self.assertTrue(np.allclose(logc4_curve(np.array([0.0, 0.18, 1.0])), np.array([-3852.359026659536, 0.4090068696819821, 0.6577136499999999])))

    def test_inverse_logc4_curve(self):
      self.assertTrue(np.allclose(inverse_logc4_curve(0.09285527796717754), np.array([0.04345044])))
      self.assertTrue(np.allclose(inverse_logc4_curve(0.4090068696819821), np.array([0.18])))
      self.assertTrue(np.allclose(inverse_logc4_curve(np.array([0.09285527796717754, 0.4090068696819821, 0.6577136499999999])), np.array([0.04345044, 0.18, 1.0])))


if __name__ == '__main__':
    unittest.main()
</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.<environment_details>
# VSCode Visible Files
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
pixelpasta/tests/test_color_analysis.py

# VSCode Open Tabs
pixelpasta/tests/test_cube_parser.py
pixelpasta/lut_processor/cube_parser.py
pixelpasta/app.py
pixelpasta/lut_processor/color_analysis.py
pixelpasta/templates/upload.html
pixelpasta/tests/test_color_analysis.py

# Current Time
19/03/2025, 6:47:05 pm (Europe/Warsaw, UTC+1:00)

# Current Mode
ACT MODE
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])))

    def test_inverse_slog3_curve(self):
        a = 0.432699
        b = 0.009468
        c = 0.655
        d = 0.037584
        e = 0.01
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), np.array([0.1])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), np.array([1.0])))
        self.assertTrue(np.allclose(inverse_slog3_curve(np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])), np.array([ (0.01 - e) / d, 0.1, 1.0])))

    def test_rec709_oetf(self):
        self.assertAlmostEqual(rec709_oetf(0.0), 0.0)
        self.assertAlmostEqual(rec709_oetf(0.018), 0.08124794403514046)
        self.assertAlmostEqual(rec709_oetf(1.0), 1.0)
        self.assertTrue(np.allclose(rec709_oetf(np.array([0.0, 0.018, 1.0])), np.array([0.0, 0.08124794403514046, 1.0])))

    def test_interpolate_1d_lut(self):
        lut_1d = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]])
        output = interpolate_1d_lut(lut_1d, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_interpolate_3d_lut(self):
        lut_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]
        ])
        lut_size = 2
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([
            [0.  , 0.  , 0.  ],
            [0.5 , 0.5 , 0.5 ],
            [1.  , 1.  , 1.  ]
        ])
        output = interpolate_3d_lut(lut_3d, lut_size, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_srgb_to_rec709(self):
        rgb_values = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        expected_output_sgamut3 = np.array([
            [ 1.641 , -0.6636,  0.0117],
            [-0.3245,  1.6157, -0.0085],
            [-0.3165,  0.0479,  0.9968]
        ])
        expected_output_sgamut3_cine = np.array([
            [ 1.5529, -0.5428, -0.0026],
            [-0.2555,  1.5027, -0.0186],
            [-0.2974,  0.0401,  1.0212]
        ])
        output_sgamut3 = srgb_to_rec709(rgb_values, 'S-Gamut3')
        output_sgamut3_cine = srgb_to_rec709(rgb_values, 'S-Gamut3.Cine')
        self.assertTrue(np.allclose(output_sgamut3, expected_output_sgamut3))
        self.assertTrue(np.allclose(output_sgamut3_cine, expected_output_sgamut3_cine))
        with self.assertRaises(ValueError):
            srgb_to_rec709(rgb_values, 'InvalidColorSpace')

    def test_generate_table(self):
        # Tworzymy tymczasowy plik .cube
        content = """
TITLE "Test LUT"
LUT_1D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as temp_file:
            temp_file.write(content.encode())
            filepath = temp_file.name

        # Testujemy dla S-Gamut3
        df_sgamut3 = generate_table(filepath, 'S-Gamut3')
        self.assertIsInstance(df_sgamut3, pd.DataFrame)
        self.assertEqual(len(df_sgamut3), 20)
        self.assertEqual(df_sgamut3['Color Space'][0], 'S-Gamut3')

        # Testujemy dla S-Gamut3.Cine
        df_sgamut3_cine = generate_table(filepath, 'S-Gamut3.Cine')
        self.assertIsInstance(df_sgamut3_cine, pd.DataFrame)
        self.assertEqual(len(df_sgamut3_cine), 20)
        self.assertEqual(df_sgamut3_cine['Color Space'][0], 'S-Gamut3.Cine')

        os.remove(filepath) # Usuwamy tymczasowy plik

    def test_logc4_curve(self):
      self.assertTrue(np.allclose(logc4_curve(0.0), np.array([-3852.359026659536])))
      self.assertAlmostEqual(logc4_curve(0.18), 0.4090068696819821)
      self.assertTrue(np.allclose(logc4_curve(np.array([0.0, 0.18, 1.0])), np.array([-3852.359026659536, 0.4090068696819821, 0.6577136499999999])))

    def test_inverse_logc4_curve(self):
      self.assertTrue(np.allclose(inverse_logc4_curve(0.09285527796717754), np.array([0.04345044])))
      self.assertTrue(np.allclose(inverse_logc4_curve(0.4090068696819821), np.array([0.18])))
      self.assertTrue(np.allclose(inverse_logc4_curve(np.array([0.09285527796717754, 0.4090068696819821, 0.6577136499999999])), np.array([0.04345044, 0.18, 1.0])))


if __name__ == '__main__':
    unittest.main()
</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.<environment_details>
# VSCode Visible Files
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
pixelpasta/tests/test_color_analysis.py

# VSCode Open Tabs
pixelpasta/tests/test_cube_parser.py
pixelpasta/lut_processor/cube_parser.py
pixelpasta/app.py
pixelpasta/lut_processor/color_analysis.py
pixelpasta/templates/upload.html
pixelpasta/tests/test_color_analysis.py

# Current Time
19/03/2025, 6:47:05 pm (Europe/Warsaw, UTC+1:00)

# Current Mode
ACT MODE
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])))

    def test_inverse_slog3_curve(self):
        a = 0.432699
        b = 0.009468
        c = 0.655
        d = 0.037584
        e = 0.01
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), np.array([0.1])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), np.array([1.0])))
        self.assertTrue(np.allclose(inverse_slog3_curve(np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])), np.array([ (0.01 - e) / d, 0.1, 1.0])))

    def test_rec709_oetf(self):
        self.assertAlmostEqual(rec709_oetf(0.0), 0.0)
        self.assertAlmostEqual(rec709_oetf(0.018), 0.08124794403514046)
        self.assertAlmostEqual(rec709_oetf(1.0), 1.0)
        self.assertTrue(np.allclose(rec709_oetf(np.array([0.0, 0.018, 1.0])), np.array([0.0, 0.08124794403514046, 1.0])))

    def test_interpolate_1d_lut(self):
        lut_1d = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]])
        output = interpolate_1d_lut(lut_1d, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_interpolate_3d_lut(self):
        lut_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]
        ])
        lut_size = 2
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([
            [0.  , 0.  , 0.  ],
            [0.5 , 0.5 , 0.5 ],
            [1.  , 1.  , 1.  ]
        ])
        output = interpolate_3d_lut(lut_3d, lut_size, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_srgb_to_rec709(self):
        rgb_values = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        expected_output_sgamut3 = np.array([
            [ 1.641 , -0.6636,  0.0117],
            [-0.3245,  1.6157, -0.0085],
            [-0.3165,  0.0479,  0.9968]
        ])
        expected_output_sgamut3_cine = np.array([
            [ 1.5529, -0.5428, -0.0026],
            [-0.2555,  1.5027, -0.0186],
            [-0.2974,  0.0401,  1.0212]
        ])
        output_sgamut3 = srgb_to_rec709(rgb_values, 'S-Gamut3')
        output_sgamut3_cine = srgb_to_rec709(rgb_values, 'S-Gamut3.Cine')
        self.assertTrue(np.allclose(output_sgamut3, expected_output_sgamut3))
        self.assertTrue(np.allclose(output_sgamut3_cine, expected_output_sgamut3_cine))
        with self.assertRaises(ValueError):
            srgb_to_rec709(rgb_values, 'InvalidColorSpace')

    def test_generate_table(self):
        # Tworzymy tymczasowy plik .cube
        content = """
TITLE "Test LUT"
LUT_1D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as temp_file:
            temp_file.write(content.encode())
            filepath = temp_file.name

        # Testujemy dla S-Gamut3
        df_sgamut3 = generate_table(filepath, 'S-Gamut3')
        self.assertIsInstance(df_sgamut3, pd.DataFrame)
        self.assertEqual(len(df_sgamut3), 20)
        self.assertEqual(df_sgamut3['Color Space'][0], 'S-Gamut3')

        # Testujemy dla S-Gamut3.Cine
        df_sgamut3_cine = generate_table(filepath, 'S-Gamut3.Cine')
        self.assertIsInstance(df_sgamut3_cine, pd.DataFrame)
        self.assertEqual(len(df_sgamut3_cine), 20)
        self.assertEqual(df_sgamut3_cine['Color Space'][0], 'S-Gamut3.Cine')

        os.remove(filepath) # Usuwamy tymczasowy plik

    def test_logc4_curve(self):
      self.assertTrue(np.allclose(logc4_curve(0.0), np.array([-3852.359026659536])))
      self.assertAlmostEqual(logc4_curve(0.18), 0.4090068696819821)
      self.assertTrue(np.allclose(logc4_curve(np.array([0.0, 0.18, 1.0])), np.array([-3852.359026659536, 0.4090068696819821, 0.6577136499999999])))

    def test_inverse_logc4_curve(self):
      self.assertTrue(np.allclose(inverse_logc4_curve(0.09285527796717754), np.array([0.04345044])))
      self.assertTrue(np.allclose(inverse_logc4_curve(0.4090068696819821), np.array([0.18])))
      self.assertTrue(np.allclose(inverse_logc4_curve(np.array([0.09285527796717754, 0.4090068696819821, 0.6577136499999999])), np.array([0.04345044, 0.18, 1.0])))


if __name__ == '__main__':
    unittest.main()
</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.<environment_details>
# VSCode Visible Files
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
pixelpasta/tests/test_color_analysis.py

# VSCode Open Tabs
pixelpasta/tests/test_cube_parser.py
pixelpasta/lut_processor/cube_parser.py
pixelpasta/app.py
pixelpasta/lut_processor/color_analysis.py
pixelpasta/templates/upload.html
pixelpasta/tests/test_color_analysis.py

# Current Time
19/03/2025, 6:47:05 pm (Europe/Warsaw, UTC+1:00)

# Current Mode
ACT MODE
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])))

    def test_inverse_slog3_curve(self):
        a = 0.432699
        b = 0.009468
        c = 0.655
        d = 0.037584
        e = 0.01
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), np.array([0.1])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), np.array([1.0])))
        self.assertTrue(np.allclose(inverse_slog3_curve(np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])), np.array([ (0.01 - e) / d, 0.1, 1.0])))

    def test_rec709_oetf(self):
        self.assertAlmostEqual(rec709_oetf(0.0), 0.0)
        self.assertAlmostEqual(rec709_oetf(0.018), 0.08124794403514046)
        self.assertAlmostEqual(rec709_oetf(1.0), 1.0)
        self.assertTrue(np.allclose(rec709_oetf(np.array([0.0, 0.018, 1.0])), np.array([0.0, 0.08124794403514046, 1.0])))

    def test_interpolate_1d_lut(self):
        lut_1d = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]])
        output = interpolate_1d_lut(lut_1d, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_interpolate_3d_lut(self):
        lut_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]
        ])
        lut_size = 2
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([
            [0.  , 0.  , 0.  ],
            [0.5 , 0.5 , 0.5 ],
            [1.  , 1.  , 1.  ]
        ])
        output = interpolate_3d_lut(lut_3d, lut_size, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_srgb_to_rec709(self):
        rgb_values = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        expected_output_sgamut3 = np.array([
            [ 1.641 , -0.6636,  0.0117],
            [-0.3245,  1.6157, -0.0085],
            [-0.3165,  0.0479,  0.9968]
        ])
        expected_output_sgamut3_cine = np.array([
            [ 1.5529, -0.5428, -0.0026],
            [-0.2555,  1.5027, -0.0186],
            [-0.2974,  0.0401,  1.0212]
        ])
        output_sgamut3 = srgb_to_rec709(rgb_values, 'S-Gamut3')
        output_sgamut3_cine = srgb_to_rec709(rgb_values, 'S-Gamut3.Cine')
        self.assertTrue(np.allclose(output_sgamut3, expected_output_sgamut3))
        self.assertTrue(np.allclose(output_sgamut3_cine, expected_output_sgamut3_cine))
        with self.assertRaises(ValueError):
            srgb_to_rec709(rgb_values, 'InvalidColorSpace')

    def test_generate_table(self):
        # Tworzymy tymczasowy plik .cube
        content = """
TITLE "Test LUT"
LUT_1D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as temp_file:
            temp_file.write(content.encode())
            filepath = temp_file.name

        # Testujemy dla S-Gamut3
        df_sgamut3 = generate_table(filepath, 'S-Gamut3')
        self.assertIsInstance(df_sgamut3, pd.DataFrame)
        self.assertEqual(len(df_sgamut3), 20)
        self.assertEqual(df_sgamut3['Color Space'][0], 'S-Gamut3')

        # Testujemy dla S-Gamut3.Cine
        df_sgamut3_cine = generate_table(filepath, 'S-Gamut3.Cine')
        self.assertIsInstance(df_sgamut3_cine, pd.DataFrame)
        self.assertEqual(len(df_sgamut3_cine), 20)
        self.assertEqual(df_sgamut3_cine['Color Space'][0], 'S-Gamut3.Cine')

        os.remove(filepath) # Usuwamy tymczasowy plik

    def test_logc4_curve(self):
      self.assertTrue(np.allclose(logc4_curve(0.0), np.array([-3852.359026659536])))
      self.assertAlmostEqual(logc4_curve(0.18), 0.4090068696819821)
      self.assertTrue(np.allclose(logc4_curve(np.array([0.0, 0.18, 1.0])), np.array([-3852.359026659536, 0.4090068696819821, 0.6577136499999999])))

    def test_inverse_logc4_curve(self):
      self.assertTrue(np.allclose(inverse_logc4_curve(0.09285527796717754), np.array([0.04345044])))
      self.assertTrue(np.allclose(inverse_logc4_curve(0.4090068696819821), np.array([0.18])))
      self.assertTrue(np.allclose(inverse_logc4_curve(np.array([0.09285527796717754, 0.4090068696819821, 0.6577136499999999])), np.array([0.04345044, 0.18, 1.0])))


if __name__ == '__main__':
    unittest.main()
</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.<environment_details>
# VSCode Visible Files
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
pixelpasta/tests/test_color_analysis.py

# VSCode Open Tabs
pixelpasta/tests/test_cube_parser.py
pixelpasta/lut_processor/cube_parser.py
pixelpasta/app.py
pixelpasta/lut_processor/color_analysis.py
pixelpasta/templates/upload.html
pixelpasta/tests/test_color_analysis.py

# Current Time
19/03/2025, 6:47:05 pm (Europe/Warsaw, UTC+1:00)

# Current Mode
ACT MODE
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])))

    def test_inverse_slog3_curve(self):
        a = 0.432699
        b = 0.009468
        c = 0.655
        d = 0.037584
        e = 0.01
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), np.array([0.1])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), np.array([1.0])))
        self.assertTrue(np.allclose(inverse_slog3_curve(np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])), np.array([ (0.01 - e) / d, 0.1, 1.0])))

    def test_rec709_oetf(self):
        self.assertAlmostEqual(rec709_oetf(0.0), 0.0)
        self.assertAlmostEqual(rec709_oetf(0.018), 0.08124794403514046)
        self.assertAlmostEqual(rec709_oetf(1.0), 1.0)
        self.assertTrue(np.allclose(rec709_oetf(np.array([0.0, 0.018, 1.0])), np.array([0.0, 0.08124794403514046, 1.0])))

    def test_interpolate_1d_lut(self):
        lut_1d = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]])
        output = interpolate_1d_lut(lut_1d, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_interpolate_3d_lut(self):
        lut_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]
        ])
        lut_size = 2
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([
            [0.  , 0.  , 0.  ],
            [0.5 , 0.5 , 0.5 ],
            [1.  , 1.  , 1.  ]
        ])
        output = interpolate_3d_lut(lut_3d, lut_size, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_srgb_to_rec709(self):
        rgb_values = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        expected_output_sgamut3 = np.array([
            [ 1.641 , -0.6636,  0.0117],
            [-0.3245,  1.6157, -0.0085],
            [-0.3165,  0.0479,  0.9968]
        ])
        expected_output_sgamut3_cine = np.array([
            [ 1.5529, -0.5428, -0.0026],
            [-0.2555,  1.5027, -0.0186],
            [-0.2974,  0.0401,  1.0212]
        ])
        output_sgamut3 = srgb_to_rec709(rgb_values, 'S-Gamut3')
        output_sgamut3_cine = srgb_to_rec709(rgb_values, 'S-Gamut3.Cine')
        self.assertTrue(np.allclose(output_sgamut3, expected_output_sgamut3))
        self.assertTrue(np.allclose(output_sgamut3_cine, expected_output_sgamut3_cine))
        with self.assertRaises(ValueError):
            srgb_to_rec709(rgb_values, 'InvalidColorSpace')

    def test_generate_table(self):
        # Tworzymy tymczasowy plik .cube
        content = """
TITLE "Test LUT"
LUT_1D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as temp_file:
            temp_file.write(content.encode())
            filepath = temp_file.name

        # Testujemy dla S-Gamut3
        df_sgamut3 = generate_table(filepath, 'S-Gamut3')
        self.assertIsInstance(df_sgamut3, pd.DataFrame)
        self.assertEqual(len(df_sgamut3), 20)
        self.assertEqual(df_sgamut3['Color Space'][0], 'S-Gamut3')

        # Testujemy dla S-Gamut3.Cine
        df_sgamut3_cine = generate_table(filepath, 'S-Gamut3.Cine')
        self.assertIsInstance(df_sgamut3_cine, pd.DataFrame)
        self.assertEqual(len(df_sgamut3_cine), 20)
        self.assertEqual(df_sgamut3_cine['Color Space'][0], 'S-Gamut3.Cine')

        os.remove(filepath) # Usuwamy tymczasowy plik

    def test_logc4_curve(self):
      self.assertTrue(np.allclose(logc4_curve(0.0), np.array([-3852.359026659536])))
      self.assertAlmostEqual(logc4_curve(0.18), 0.4090068696819821)
      self.assertTrue(np.allclose(logc4_curve(np.array([0.0, 0.18, 1.0])), np.array([-3852.359026659536, 0.4090068696819821, 0.6577136499999999])))

    def test_inverse_logc4_curve(self):
      self.assertTrue(np.allclose(inverse_logc4_curve(0.09285527796717754), np.array([0.04345044])))
      self.assertTrue(np.allclose(inverse_logc4_curve(0.4090068696819821), np.array([0.18])))
      self.assertTrue(np.allclose(inverse_logc4_curve(np.array([0.09285527796717754, 0.4090068696819821, 0.6577136499999999])), np.array([0.04345044, 0.18, 1.0])))


if __name__ == '__main__':
    unittest.main()
</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.<environment_details>
# VSCode Visible Files
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
pixelpasta/tests/test_color_analysis.py

# VSCode Open Tabs
pixelpasta/tests/test_cube_parser.py
pixelpasta/lut_processor/cube_parser.py
pixelpasta/app.py
pixelpasta/lut_processor/color_analysis.py
pixelpasta/templates/upload.html
pixelpasta/tests/test_color_analysis.py

# Current Time
19/03/2025, 6:47:05 pm (Europe/Warsaw, UTC+1:00)

# Current Mode
ACT MODE
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])))

    def test_inverse_slog3_curve(self):
        a = 0.432699
        b = 0.009468
        c = 0.655
        d = 0.037584
        e = 0.01
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), np.array([0.1])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), np.array([1.0])))
        self.assertTrue(np.allclose(inverse_slog3_curve(np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])), np.array([ (0.01 - e) / d, 0.1, 1.0])))

    def test_rec709_oetf(self):
        self.assertAlmostEqual(rec709_oetf(0.0), 0.0)
        self.assertAlmostEqual(rec709_oetf(0.018), 0.08124794403514046)
        self.assertAlmostEqual(rec709_oetf(1.0), 1.0)
        self.assertTrue(np.allclose(rec709_oetf(np.array([0.0, 0.018, 1.0])), np.array([0.0, 0.08124794403514046, 1.0])))

    def test_interpolate_1d_lut(self):
        lut_1d = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]])
        output = interpolate_1d_lut(lut_1d, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_interpolate_3d_lut(self):
        lut_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]
        ])
        lut_size = 2
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([
            [0.  , 0.  , 0.  ],
            [0.5 , 0.5 , 0.5 ],
            [1.  , 1.  , 1.  ]
        ])
        output = interpolate_3d_lut(lut_3d, lut_size, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_srgb_to_rec709(self):
        rgb_values = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        expected_output_sgamut3 = np.array([
            [ 1.641 , -0.6636,  0.0117],
            [-0.3245,  1.6157, -0.0085],
            [-0.3165,  0.0479,  0.9968]
        ])
        expected_output_sgamut3_cine = np.array([
            [ 1.5529, -0.5428, -0.0026],
            [-0.2555,  1.5027, -0.0186],
            [-0.2974,  0.0401,  1.0212]
        ])
        output_sgamut3 = srgb_to_rec709(rgb_values, 'S-Gamut3')
        output_sgamut3_cine = srgb_to_rec709(rgb_values, 'S-Gamut3.Cine')
        self.assertTrue(np.allclose(output_sgamut3, expected_output_sgamut3))
        self.assertTrue(np.allclose(output_sgamut3_cine, expected_output_sgamut3_cine))
        with self.assertRaises(ValueError):
            srgb_to_rec709(rgb_values, 'InvalidColorSpace')

    def test_generate_table(self):
        # Tworzymy tymczasowy plik .cube
        content = """
TITLE "Test LUT"
LUT_1D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as temp_file:
            temp_file.write(content.encode())
            filepath = temp_file.name

        # Testujemy dla S-Gamut3
        df_sgamut3 = generate_table(filepath, 'S-Gamut3')
        self.assertIsInstance(df_sgamut3, pd.DataFrame)
        self.assertEqual(len(df_sgamut3), 20)
        self.assertEqual(df_sgamut3['Color Space'][0], 'S-Gamut3')

        # Testujemy dla S-Gamut3.Cine
        df_sgamut3_cine = generate_table(filepath, 'S-Gamut3.Cine')
        self.assertIsInstance(df_sgamut3_cine, pd.DataFrame)
        self.assertEqual(len(df_sgamut3_cine), 20)
        self.assertEqual(df_sgamut3_cine['Color Space'][0], 'S-Gamut3.Cine')

        os.remove(filepath) # Usuwamy tymczasowy plik

    def test_logc4_curve(self):
      self.assertTrue(np.allclose(logc4_curve(0.0), np.array([-3852.359026659536])))
      self.assertAlmostEqual(logc4_curve(0.18), 0.4090068696819821)
      self.assertTrue(np.allclose(logc4_curve(np.array([0.0, 0.18, 1.0])), np.array([-3852.359026659536, 0.4090068696819821, 0.6577136499999999])))

    def test_inverse_logc4_curve(self):
      self.assertTrue(np.allclose(inverse_logc4_curve(0.09285527796717754), np.array([0.04345044])))
      self.assertTrue(np.allclose(inverse_logc4_curve(0.4090068696819821), np.array([0.18])))
      self.assertTrue(np.allclose(inverse_logc4_curve(np.array([0.09285527796717754, 0.4090068696819821, 0.6577136499999999])), np.array([0.04345044, 0.18, 1.0])))


if __name__ == '__main__':
    unittest.main()
</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.<environment_details>
# VSCode Visible Files
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
pixelpasta/tests/test_color_analysis.py

# VSCode Open Tabs
pixelpasta/tests/test_cube_parser.py
pixelpasta/lut_processor/cube_parser.py
pixelpasta/app.py
pixelpasta/lut_processor/color_analysis.py
pixelpasta/templates/upload.html
pixelpasta/tests/test_color_analysis.py

# Current Time
19/03/2025, 6:47:05 pm (Europe/Warsaw, UTC+1:00)

# Current Mode
ACT MODE
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])))

    def test_inverse_slog3_curve(self):
        a = 0.432699
        b = 0.009468
        c = 0.655
        d = 0.037584
        e = 0.01
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), np.array([0.1])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), np.array([1.0])))
        self.assertTrue(np.allclose(inverse_slog3_curve(np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])), np.array([ (0.01 - e) / d, 0.1, 1.0])))

    def test_rec709_oetf(self):
        self.assertAlmostEqual(rec709_oetf(0.0), 0.0)
        self.assertAlmostEqual(rec709_oetf(0.018), 0.08124794403514046)
        self.assertAlmostEqual(rec709_oetf(1.0), 1.0)
        self.assertTrue(np.allclose(rec709_oetf(np.array([0.0, 0.018, 1.0])), np.array([0.0, 0.08124794403514046, 1.0])))

    def test_interpolate_1d_lut(self):
        lut_1d = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]])
        output = interpolate_1d_lut(lut_1d, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_interpolate_3d_lut(self):
        lut_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]
        ])
        lut_size = 2
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([
            [0.  , 0.  , 0.  ],
            [0.5 , 0.5 , 0.5 ],
            [1.  , 1.  , 1.  ]
        ])
        output = interpolate_3d_lut(lut_3d, lut_size, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_srgb_to_rec709(self):
        rgb_values = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        expected_output_sgamut3 = np.array([
            [ 1.641 , -0.6636,  0.0117],
            [-0.3245,  1.6157, -0.0085],
            [-0.3165,  0.0479,  0.9968]
        ])
        expected_output_sgamut3_cine = np.array([
            [ 1.5529, -0.5428, -0.0026],
            [-0.2555,  1.5027, -0.0186],
            [-0.2974,  0.0401,  1.0212]
        ])
        output_sgamut3 = srgb_to_rec709(rgb_values, 'S-Gamut3')
        output_sgamut3_cine = srgb_to_rec709(rgb_values, 'S-Gamut3.Cine')
        self.assertTrue(np.allclose(output_sgamut3, expected_output_sgamut3))
        self.assertTrue(np.allclose(output_sgamut3_cine, expected_output_sgamut3_cine))
        with self.assertRaises(ValueError):
            srgb_to_rec709(rgb_values, 'InvalidColorSpace')

    def test_generate_table(self):
        # Tworzymy tymczasowy plik .cube
        content = """
TITLE "Test LUT"
LUT_1D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as temp_file:
            temp_file.write(content.encode())
            filepath = temp_file.name

        # Testujemy dla S-Gamut3
        df_sgamut3 = generate_table(filepath, 'S-Gamut3')
        self.assertIsInstance(df_sgamut3, pd.DataFrame)
        self.assertEqual(len(df_sgamut3), 20)
        self.assertEqual(df_sgamut3['Color Space'][0], 'S-Gamut3')

        # Testujemy dla S-Gamut3.Cine
        df_sgamut3_cine = generate_table(filepath, 'S-Gamut3.Cine')
        self.assertIsInstance(df_sgamut3_cine, pd.DataFrame)
        self.assertEqual(len(df_sgamut3_cine), 20)
        self.assertEqual(df_sgamut3_cine['Color Space'][0], 'S-Gamut3.Cine')

        os.remove(filepath) # Usuwamy tymczasowy plik

    def test_logc4_curve(self):
      self.assertTrue(np.allclose(logc4_curve(0.0), np.array([-3852.359026659536])))
      self.assertAlmostEqual(logc4_curve(0.18), 0.4090068696819821)
      self.assertTrue(np.allclose(logc4_curve(np.array([0.0, 0.18, 1.0])), np.array([-3852.359026659536, 0.4090068696819821, 0.6577136499999999])))

    def test_inverse_logc4_curve(self):
      self.assertTrue(np.allclose(inverse_logc4_curve(0.09285527796717754), np.array([0.04345044])))
      self.assertTrue(np.allclose(inverse_logc4_curve(0.4090068696819821), np.array([0.18])))
      self.assertTrue(np.allclose(inverse_logc4_curve(np.array([0.09285527796717754, 0.4090068696819821, 0.6577136499999999])), np.array([0.04345044, 0.18, 1.0])))


if __name__ == '__main__':
    unittest.main()
</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.<environment_details>
# VSCode Visible Files
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
pixelpasta/tests/test_color_analysis.py

# VSCode Open Tabs
pixelpasta/tests/test_cube_parser.py
pixelpasta/lut_processor/cube_parser.py
pixelpasta/app.py
pixelpasta/lut_processor/color_analysis.py
pixelpasta/templates/upload.html
pixelpasta/tests/test_color_analysis.py

# Current Time
19/03/2025, 6:47:05 pm (Europe/Warsaw, UTC+1:00)

# Current Mode
ACT MODE
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])))

    def test_inverse_slog3_curve(self):
        a = 0.432699
        b = 0.009468
        c = 0.655
        d = 0.037584
        e = 0.01
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), np.array([0.1])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), np.array([1.0])))
        self.assertTrue(np.allclose(inverse_slog3_curve(np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])), np.array([ (0.01 - e) / d, 0.1, 1.0])))

    def test_rec709_oetf(self):
        self.assertAlmostEqual(rec709_oetf(0.0), 0.0)
        self.assertAlmostEqual(rec709_oetf(0.018), 0.08124794403514046)
        self.assertAlmostEqual(rec709_oetf(1.0), 1.0)
        self.assertTrue(np.allclose(rec709_oetf(np.array([0.0, 0.018, 1.0])), np.array([0.0, 0.08124794403514046, 1.0])))

    def test_interpolate_1d_lut(self):
        lut_1d = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]])
        output = interpolate_1d_lut(lut_1d, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_interpolate_3d_lut(self):
        lut_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]
        ])
        lut_size = 2
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([
            [0.  , 0.  , 0.  ],
            [0.5 , 0.5 , 0.5 ],
            [1.  , 1.  , 1.  ]
        ])
        output = interpolate_3d_lut(lut_3d, lut_size, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_srgb_to_rec709(self):
        rgb_values = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        expected_output_sgamut3 = np.array([
            [ 1.641 , -0.6636,  0.0117],
            [-0.3245,  1.6157, -0.0085],
            [-0.3165,  0.0479,  0.9968]
        ])
        expected_output_sgamut3_cine = np.array([
            [ 1.5529, -0.5428, -0.0026],
            [-0.2555,  1.5027, -0.0186],
            [-0.2974,  0.0401,  1.0212]
        ])
        output_sgamut3 = srgb_to_rec709(rgb_values, 'S-Gamut3')
        output_sgamut3_cine = srgb_to_rec709(rgb_values, 'S-Gamut3.Cine')
        self.assertTrue(np.allclose(output_sgamut3, expected_output_sgamut3))
        self.assertTrue(np.allclose(output_sgamut3_cine, expected_output_sgamut3_cine))
        with self.assertRaises(ValueError):
            srgb_to_rec709(rgb_values, 'InvalidColorSpace')

    def test_generate_table(self):
        # Tworzymy tymczasowy plik .cube
        content = """
TITLE "Test LUT"
LUT_1D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as temp_file:
            temp_file.write(content.encode())
            filepath = temp_file.name

        # Testujemy dla S-Gamut3
        df_sgamut3 = generate_table(filepath, 'S-Gamut3')
        self.assertIsInstance(df_sgamut3, pd.DataFrame)
        self.assertEqual(len(df_sgamut3), 20)
        self.assertEqual(df_sgamut3['Color Space'][0], 'S-Gamut3')

        # Testujemy dla S-Gamut3.Cine
        df_sgamut3_cine = generate_table(filepath, 'S-Gamut3.Cine')
        self.assertIsInstance(df_sgamut3_cine, pd.DataFrame)
        self.assertEqual(len(df_sgamut3_cine), 20)
        self.assertEqual(df_sgamut3_cine['Color Space'][0], 'S-Gamut3.Cine')

        os.remove(filepath) # Usuwamy tymczasowy plik

    def test_logc4_curve(self):
      self.assertTrue(np.allclose(logc4_curve(0.0), np.array([-3852.359026659536])))
      self.assertAlmostEqual(logc4_curve(0.18), 0.4090068696819821)
      self.assertTrue(np.allclose(logc4_curve(np.array([0.0, 0.18, 1.0])), np.array([-3852.359026659536, 0.4090068696819821, 0.6577136499999999])))

    def test_inverse_logc4_curve(self):
      self.assertTrue(np.allclose(inverse_logc4_curve(0.09285527796717754), np.array([0.04345044])))
      self.assertTrue(np.allclose(inverse_logc4_curve(0.4090068696819821), np.array([0.18])))
      self.assertTrue(np.allclose(inverse_logc4_curve(np.array([0.09285527796717754, 0.4090068696819821, 0.6577136499999999])), np.array([0.04345044, 0.18, 1.0])))


if __name__ == '__main__':
    unittest.main()
</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.<environment_details>
# VSCode Visible Files
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
pixelpasta/tests/test_color_analysis.py

# VSCode Open Tabs
pixelpasta/tests/test_cube_parser.py
pixelpasta/lut_processor/cube_parser.py
pixelpasta/app.py
pixelpasta/lut_processor/color_analysis.py
pixelpasta/templates/upload.html
pixelpasta/tests/test_color_analysis.py

# Current Time
19/03/2025, 6:47:05 pm (Europe/Warsaw, UTC+1:00)

# Current Mode
ACT MODE
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])))

    def test_inverse_slog3_curve(self):
        a = 0.432699
        b = 0.009468
        c = 0.655
        d = 0.037584
        e = 0.01
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), np.array([0.1])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), np.array([1.0])))
        self.assertTrue(np.allclose(inverse_slog3_curve(np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])), np.array([ (0.01 - e) / d, 0.1, 1.0])))

    def test_rec709_oetf(self):
        self.assertAlmostEqual(rec709_oetf(0.0), 0.0)
        self.assertAlmostEqual(rec709_oetf(0.018), 0.08124794403514046)
        self.assertAlmostEqual(rec709_oetf(1.0), 1.0)
        self.assertTrue(np.allclose(rec709_oetf(np.array([0.0, 0.018, 1.0])), np.array([0.0, 0.08124794403514046, 1.0])))

    def test_interpolate_1d_lut(self):
        lut_1d = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]])
        output = interpolate_1d_lut(lut_1d, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_interpolate_3d_lut(self):
        lut_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]
        ])
        lut_size = 2
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([
            [0.  , 0.  , 0.  ],
            [0.5 , 0.5 , 0.5 ],
            [1.  , 1.  , 1.  ]
        ])
        output = interpolate_3d_lut(lut_3d, lut_size, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_srgb_to_rec709(self):
        rgb_values = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        expected_output_sgamut3 = np.array([
            [ 1.641 , -0.6636,  0.0117],
            [-0.3245,  1.6157, -0.0085],
            [-0.3165,  0.0479,  0.9968]
        ])
        expected_output_sgamut3_cine = np.array([
            [ 1.5529, -0.5428, -0.0026],
            [-0.2555,  1.5027, -0.0186],
            [-0.2974,  0.0401,  1.0212]
        ])
        output_sgamut3 = srgb_to_rec709(rgb_values, 'S-Gamut3')
        output_sgamut3_cine = srgb_to_rec709(rgb_values, 'S-Gamut3.Cine')
        self.assertTrue(np.allclose(output_sgamut3, expected_output_sgamut3))
        self.assertTrue(np.allclose(output_sgamut3_cine, expected_output_sgamut3_cine))
        with self.assertRaises(ValueError):
            srgb_to_rec709(rgb_values, 'InvalidColorSpace')

    def test_generate_table(self):
        # Tworzymy tymczasowy plik .cube
        content = """
TITLE "Test LUT"
LUT_1D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as temp_file:
            temp_file.write(content.encode())
            filepath = temp_file.name

        # Testujemy dla S-Gamut3
        df_sgamut3 = generate_table(filepath, 'S-Gamut3')
        self.assertIsInstance(df_sgamut3, pd.DataFrame)
        self.assertEqual(len(df_sgamut3), 20)
        self.assertEqual(df_sgamut3['Color Space'][0], 'S-Gamut3')

        # Testujemy dla S-Gamut3.Cine
        df_sgamut3_cine = generate_table(filepath, 'S-Gamut3.Cine')
        self.assertIsInstance(df_sgamut3_cine, pd.DataFrame)
        self.assertEqual(len(df_sgamut3_cine), 20)
        self.assertEqual(df_sgamut3_cine['Color Space'][0], 'S-Gamut3.Cine')

        os.remove(filepath) # Usuwamy tymczasowy plik

    def test_logc4_curve(self):
      self.assertTrue(np.allclose(logc4_curve(0.0), np.array([-3852.359026659536])))
      self.assertAlmostEqual(logc4_curve(0.18), 0.4090068696819821)
      self.assertTrue(np.allclose(logc4_curve(np.array([0.0, 0.18, 1.0])), np.array([-3852.359026659536, 0.4090068696819821, 0.6577136499999999])))

    def test_inverse_logc4_curve(self):
      self.assertTrue(np.allclose(inverse_logc4_curve(0.09285527796717754), np.array([0.04345044])))
      self.assertTrue(np.allclose(inverse_logc4_curve(0.4090068696819821), np.array([0.18])))
      self.assertTrue(np.allclose(inverse_logc4_curve(np.array([0.09285527796717754, 0.4090068696819821, 0.6577136499999999])), np.array([0.04345044, 0.18, 1.0])))


if __name__ == '__main__':
    unittest.main()
</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.<environment_details>
# VSCode Visible Files
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
pixelpasta/tests/test_color_analysis.py

# VSCode Open Tabs
pixelpasta/tests/test_cube_parser.py
pixelpasta/lut_processor/cube_parser.py
pixelpasta/app.py
pixelpasta/lut_processor/color_analysis.py
pixelpasta/templates/upload.html
pixelpasta/tests/test_color_analysis.py

# Current Time
19/03/2025, 6:47:05 pm (Europe/Warsaw, UTC+1:00)

# Current Mode
ACT MODE
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])))

    def test_inverse_slog3_curve(self):
        a = 0.432699
        b = 0.009468
        c = 0.655
        d = 0.037584
        e = 0.01
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), np.array([0.1])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), np.array([1.0])))
        self.assertTrue(np.allclose(inverse_slog3_curve(np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])), np.array([ (0.01 - e) / d, 0.1, 1.0])))

    def test_rec709_oetf(self):
        self.assertAlmostEqual(rec709_oetf(0.0), 0.0)
        self.assertAlmostEqual(rec709_oetf(0.018), 0.08124794403514046)
        self.assertAlmostEqual(rec709_oetf(1.0), 1.0)
        self.assertTrue(np.allclose(rec709_oetf(np.array([0.0, 0.018, 1.0])), np.array([0.0, 0.08124794403514046, 1.0])))

    def test_interpolate_1d_lut(self):
        lut_1d = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]])
        output = interpolate_1d_lut(lut_1d, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_interpolate_3d_lut(self):
        lut_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]
        ])
        lut_size = 2
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([
            [0.  , 0.  , 0.  ],
            [0.5 , 0.5 , 0.5 ],
            [1.  , 1.  , 1.  ]
        ])
        output = interpolate_3d_lut(lut_3d, lut_size, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_srgb_to_rec709(self):
        rgb_values = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        expected_output_sgamut3 = np.array([
            [ 1.641 , -0.6636,  0.0117],
            [-0.3245,  1.6157, -0.0085],
            [-0.3165,  0.0479,  0.9968]
        ])
        expected_output_sgamut3_cine = np.array([
            [ 1.5529, -0.5428, -0.0026],
            [-0.2555,  1.5027, -0.0186],
            [-0.2974,  0.0401,  1.0212]
        ])
        output_sgamut3 = srgb_to_rec709(rgb_values, 'S-Gamut3')
        output_sgamut3_cine = srgb_to_rec709(rgb_values, 'S-Gamut3.Cine')
        self.assertTrue(np.allclose(output_sgamut3, expected_output_sgamut3))
        self.assertTrue(np.allclose(output_sgamut3_cine, expected_output_sgamut3_cine))
        with self.assertRaises(ValueError):
            srgb_to_rec709(rgb_values, 'InvalidColorSpace')

    def test_generate_table(self):
        # Tworzymy tymczasowy plik .cube
        content = """
TITLE "Test LUT"
LUT_1D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as temp_file:
            temp_file.write(content.encode())
            filepath = temp_file.name

        # Testujemy dla S-Gamut3
        df_sgamut3 = generate_table(filepath, 'S-Gamut3')
        self.assertIsInstance(df_sgamut3, pd.DataFrame)
        self.assertEqual(len(df_sgamut3), 20)
        self.assertEqual(df_sgamut3['Color Space'][0], 'S-Gamut3')

        # Testujemy dla S-Gamut3.Cine
        df_sgamut3_cine = generate_table(filepath, 'S-Gamut3.Cine')
        self.assertIsInstance(df_sgamut3_cine, pd.DataFrame)
        self.assertEqual(len(df_sgamut3_cine), 20)
        self.assertEqual(df_sgamut3_cine['Color Space'][0], 'S-Gamut3.Cine')

        os.remove(filepath) # Usuwamy tymczasowy plik

    def test_logc4_curve(self):
      self.assertTrue(np.allclose(logc4_curve(0.0), np.array([-3852.359026659536])))
      self.assertAlmostEqual(logc4_curve(0.18), 0.4090068696819821)
      self.assertTrue(np.allclose(logc4_curve(np.array([0.0, 0.18, 1.0])), np.array([-3852.359026659536, 0.4090068696819821, 0.6577136499999999])))

    def test_inverse_logc4_curve(self):
      self.assertTrue(np.allclose(inverse_logc4_curve(0.09285527796717754), np.array([0.04345044])))
      self.assertTrue(np.allclose(inverse_logc4_curve(0.4090068696819821), np.array([0.18])))
      self.assertTrue(np.allclose(inverse_logc4_curve(np.array([0.09285527796717754, 0.4090068696819821, 0.6577136499999999])), np.array([0.04345044, 0.18, 1.0])))


if __name__ == '__main__':
    unittest.main()
</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.<environment_details>
# VSCode Visible Files
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
pixelpasta/tests/test_color_analysis.py

# VSCode Open Tabs
pixelpasta/tests/test_cube_parser.py
pixelpasta/lut_processor/cube_parser.py
pixelpasta/app.py
pixelpasta/lut_processor/color_analysis.py
pixelpasta/templates/upload.html
pixelpasta/tests/test_color_analysis.py

# Current Time
19/03/2025, 6:47:05 pm (Europe/Warsaw, UTC+1:00)

# Current Mode
ACT MODE
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])))

    def test_inverse_slog3_curve(self):
        a = 0.432699
        b = 0.009468
        c = 0.655
        d = 0.037584
        e = 0.01
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), np.array([0.1])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), np.array([1.0])))
        self.assertTrue(np.allclose(inverse_slog3_curve(np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])), np.array([ (0.01 - e) / d, 0.1, 1.0])))

    def test_rec709_oetf(self):
        self.assertAlmostEqual(rec709_oetf(0.0), 0.0)
        self.assertAlmostEqual(rec709_oetf(0.018), 0.08124794403514046)
        self.assertAlmostEqual(rec709_oetf(1.0), 1.0)
        self.assertTrue(np.allclose(rec709_oetf(np.array([0.0, 0.018, 1.0])), np.array([0.0, 0.08124794403514046, 1.0])))

    def test_interpolate_1d_lut(self):
        lut_1d = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]])
        output = interpolate_1d_lut(lut_1d, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_interpolate_3d_lut(self):
        lut_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]
        ])
        lut_size = 2
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([
            [0.  , 0.  , 0.  ],
            [0.5 , 0.5 , 0.5 ],
            [1.  , 1.  , 1.  ]
        ])
        output = interpolate_3d_lut(lut_3d, lut_size, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_srgb_to_rec709(self):
        rgb_values = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        expected_output_sgamut3 = np.array([
            [ 1.641 , -0.6636,  0.0117],
            [-0.3245,  1.6157, -0.0085],
            [-0.3165,  0.0479,  0.9968]
        ])
        expected_output_sgamut3_cine = np.array([
            [ 1.5529, -0.5428, -0.0026],
            [-0.2555,  1.5027, -0.0186],
            [-0.2974,  0.0401,  1.0212]
        ])
        output_sgamut3 = srgb_to_rec709(rgb_values, 'S-Gamut3')
        output_sgamut3_cine = srgb_to_rec709(rgb_values, 'S-Gamut3.Cine')
        self.assertTrue(np.allclose(output_sgamut3, expected_output_sgamut3))
        self.assertTrue(np.allclose(output_sgamut3_cine, expected_output_sgamut3_cine))
        with self.assertRaises(ValueError):
            srgb_to_rec709(rgb_values, 'InvalidColorSpace')

    def test_generate_table(self):
        # Tworzymy tymczasowy plik .cube
        content = """
TITLE "Test LUT"
LUT_1D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as temp_file:
            temp_file.write(content.encode())
            filepath = temp_file.name

        # Testujemy dla S-Gamut3
        df_sgamut3 = generate_table(filepath, 'S-Gamut3')
        self.assertIsInstance(df_sgamut3, pd.DataFrame)
        self.assertEqual(len(df_sgamut3), 20)
        self.assertEqual(df_sgamut3['Color Space'][0], 'S-Gamut3')

        # Testujemy dla S-Gamut3.Cine
        df_sgamut3_cine = generate_table(filepath, 'S-Gamut3.Cine')
        self.assertIsInstance(df_sgamut3_cine, pd.DataFrame)
        self.assertEqual(len(df_sgamut3_cine), 20)
        self.assertEqual(df_sgamut3_cine['Color Space'][0], 'S-Gamut3.Cine')

        os.remove(filepath) # Usuwamy tymczasowy plik

    def test_logc4_curve(self):
      self.assertTrue(np.allclose(logc4_curve(0.0), np.array([-3852.359026659536])))
      self.assertAlmostEqual(logc4_curve(0.18), 0.4090068696819821)
      self.assertTrue(np.allclose(logc4_curve(np.array([0.0, 0.18, 1.0])), np.array([-3852.359026659536, 0.4090068696819821, 0.6577136499999999])))

    def test_inverse_logc4_curve(self):
      self.assertTrue(np.allclose(inverse_logc4_curve(0.09285527796717754), np.array([0.04345044])))
      self.assertTrue(np.allclose(inverse_logc4_curve(0.4090068696819821), np.array([0.18])))
      self.assertTrue(np.allclose(inverse_logc4_curve(np.array([0.09285527796717754, 0.4090068696819821, 0.6577136499999999])), np.array([0.04345044, 0.18, 1.0])))


if __name__ == '__main__':
    unittest.main()
</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.<environment_details>
# VSCode Visible Files
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
pixelpasta/tests/test_color_analysis.py

# VSCode Open Tabs
pixelpasta/tests/test_cube_parser.py
pixelpasta/lut_processor/cube_parser.py
pixelpasta/app.py
pixelpasta/lut_processor/color_analysis.py
pixelpasta/templates/upload.html
pixelpasta/tests/test_color_analysis.py

# Current Time
19/03/2025, 6:47:05 pm (Europe/Warsaw, UTC+1:00)

# Current Mode
ACT MODE
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])))

    def test_inverse_slog3_curve(self):
        a = 0.432699
        b = 0.009468
        c = 0.655
        d = 0.037584
        e = 0.01
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), np.array([0.1])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), np.array([1.0])))
        self.assertTrue(np.allclose(inverse_slog3_curve(np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])), np.array([ (0.01 - e) / d, 0.1, 1.0])))

    def test_rec709_oetf(self):
        self.assertAlmostEqual(rec709_oetf(0.0), 0.0)
        self.assertAlmostEqual(rec709_oetf(0.018), 0.08124794403514046)
        self.assertAlmostEqual(rec709_oetf(1.0), 1.0)
        self.assertTrue(np.allclose(rec709_oetf(np.array([0.0, 0.018, 1.0])), np.array([0.0, 0.08124794403514046, 1.0])))

    def test_interpolate_1d_lut(self):
        lut_1d = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]])
        output = interpolate_1d_lut(lut_1d, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_interpolate_3d_lut(self):
        lut_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]
        ])
        lut_size = 2
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([
            [0.  , 0.  , 0.  ],
            [0.5 , 0.5 , 0.5 ],
            [1.  , 1.  , 1.  ]
        ])
        output = interpolate_3d_lut(lut_3d, lut_size, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_srgb_to_rec709(self):
        rgb_values = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        expected_output_sgamut3 = np.array([
            [ 1.641 , -0.6636,  0.0117],
            [-0.3245,  1.6157, -0.0085],
            [-0.3165,  0.0479,  0.9968]
        ])
        expected_output_sgamut3_cine = np.array([
            [ 1.5529, -0.5428, -0.0026],
            [-0.2555,  1.5027, -0.0186],
            [-0.2974,  0.0401,  1.0212]
        ])
        output_sgamut3 = srgb_to_rec709(rgb_values, 'S-Gamut3')
        output_sgamut3_cine = srgb_to_rec709(rgb_values, 'S-Gamut3.Cine')
        self.assertTrue(np.allclose(output_sgamut3, expected_output_sgamut3))
        self.assertTrue(np.allclose(output_sgamut3_cine, expected_output_sgamut3_cine))
        with self.assertRaises(ValueError):
            srgb_to_rec709(rgb_values, 'InvalidColorSpace')

    def test_generate_table(self):
        # Tworzymy tymczasowy plik .cube
        content = """
TITLE "Test LUT"
LUT_1D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as temp_file:
            temp_file.write(content.encode())
            filepath = temp_file.name

        # Testujemy dla S-Gamut3
        df_sgamut3 = generate_table(filepath, 'S-Gamut3')
        self.assertIsInstance(df_sgamut3, pd.DataFrame)
        self.assertEqual(len(df_sgamut3), 20)
        self.assertEqual(df_sgamut3['Color Space'][0], 'S-Gamut3')

        # Testujemy dla S-Gamut3.Cine
        df_sgamut3_cine = generate_table(filepath, 'S-Gamut3.Cine')
        self.assertIsInstance(df_sgamut3_cine, pd.DataFrame)
        self.assertEqual(len(df_sgamut3_cine), 20)
        self.assertEqual(df_sgamut3_cine['Color Space'][0], 'S-Gamut3.Cine')

        os.remove(filepath) # Usuwamy tymczasowy plik

    def test_logc4_curve(self):
      self.assertTrue(np.allclose(logc4_curve(0.0), np.array([-3852.359026659536])))
      self.assertAlmostEqual(logc4_curve(0.18), 0.4090068696819821)
      self.assertTrue(np.allclose(logc4_curve(np.array([0.0, 0.18, 1.0])), np.array([-3852.359026659536, 0.4090068696819821, 0.6577136499999999])))

    def test_inverse_logc4_curve(self):
      self.assertTrue(np.allclose(inverse_logc4_curve(0.09285527796717754), np.array([0.04345044])))
      self.assertTrue(np.allclose(inverse_logc4_curve(0.4090068696819821), np.array([0.18])))
      self.assertTrue(np.allclose(inverse_logc4_curve(np.array([0.09285527796717754, 0.4090068696819821, 0.6577136499999999])), np.array([0.04345044, 0.18, 1.0])))


if __name__ == '__main__':
    unittest.main()
</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.<environment_details>
# VSCode Visible Files
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
pixelpasta/tests/test_color_analysis.py

# VSCode Open Tabs
pixelpasta/tests/test_cube_parser.py
pixelpasta/lut_processor/cube_parser.py
pixelpasta/app.py
pixelpasta/lut_processor/color_analysis.py
pixelpasta/templates/upload.html
pixelpasta/tests/test_color_analysis.py

# Current Time
19/03/2025, 6:47:05 pm (Europe/Warsaw, UTC+1:00)

# Current Mode
ACT MODE
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])))

    def test_inverse_slog3_curve(self):
        a = 0.432699
        b = 0.009468
        c = 0.655
        d = 0.037584
        e = 0.01
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), np.array([0.1])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), np.array([1.0])))
        self.assertTrue(np.allclose(inverse_slog3_curve(np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])), np.array([ (0.01 - e) / d, 0.1, 1.0])))

    def test_rec709_oetf(self):
        self.assertAlmostEqual(rec709_oetf(0.0), 0.0)
        self.assertAlmostEqual(rec709_oetf(0.018), 0.08124794403514046)
        self.assertAlmostEqual(rec709_oetf(1.0), 1.0)
        self.assertTrue(np.allclose(rec709_oetf(np.array([0.0, 0.018, 1.0])), np.array([0.0, 0.08124794403514046, 1.0])))

    def test_interpolate_1d_lut(self):
        lut_1d = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]])
        output = interpolate_1d_lut(lut_1d, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_interpolate_3d_lut(self):
        lut_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]
        ])
        lut_size = 2
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([
            [0.  , 0.  , 0.  ],
            [0.5 , 0.5 , 0.5 ],
            [1.  , 1.  , 1.  ]
        ])
        output = interpolate_3d_lut(lut_3d, lut_size, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_srgb_to_rec709(self):
        rgb_values = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        expected_output_sgamut3 = np.array([
            [ 1.641 , -0.6636,  0.0117],
            [-0.3245,  1.6157, -0.0085],
            [-0.3165,  0.0479,  0.9968]
        ])
        expected_output_sgamut3_cine = np.array([
            [ 1.5529, -0.5428, -0.0026],
            [-0.2555,  1.5027, -0.0186],
            [-0.2974,  0.0401,  1.0212]
        ])
        output_sgamut3 = srgb_to_rec709(rgb_values, 'S-Gamut3')
        output_sgamut3_cine = srgb_to_rec709(rgb_values, 'S-Gamut3.Cine')
        self.assertTrue(np.allclose(output_sgamut3, expected_output_sgamut3))
        self.assertTrue(np.allclose(output_sgamut3_cine, expected_output_sgamut3_cine))
        with self.assertRaises(ValueError):
            srgb_to_rec709(rgb_values, 'InvalidColorSpace')

    def test_generate_table(self):
        # Tworzymy tymczasowy plik .cube
        content = """
TITLE "Test LUT"
LUT_1D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as temp_file:
            temp_file.write(content.encode())
            filepath = temp_file.name

        # Testujemy dla S-Gamut3
        df_sgamut3 = generate_table(filepath, 'S-Gamut3')
        self.assertIsInstance(df_sgamut3, pd.DataFrame)
        self.assertEqual(len(df_sgamut3), 20)
        self.assertEqual(df_sgamut3['Color Space'][0], 'S-Gamut3')

        # Testujemy dla S-Gamut3.Cine
        df_sgamut3_cine = generate_table(filepath, 'S-Gamut3.Cine')
        self.assertIsInstance(df_sgamut3_cine, pd.DataFrame)
        self.assertEqual(len(df_sgamut3_cine), 20)
        self.assertEqual(df_sgamut3_cine['Color Space'][0], 'S-Gamut3.Cine')

        os.remove(filepath) # Usuwamy tymczasowy plik

    def test_logc4_curve(self):
      self.assertTrue(np.allclose(logc4_curve(0.0), np.array([-3852.359026659536])))
      self.assertAlmostEqual(logc4_curve(0.18), 0.4090068696819821)
      self.assertTrue(np.allclose(logc4_curve(np.array([0.0, 0.18, 1.0])), np.array([-3852.359026659536, 0.4090068696819821, 0.6577136499999999])))

    def test_inverse_logc4_curve(self):
      self.assertTrue(np.allclose(inverse_logc4_curve(0.09285527796717754), np.array([0.04345044])))
      self.assertTrue(np.allclose(inverse_logc4_curve(0.4090068696819821), np.array([0.18])))
      self.assertTrue(np.allclose(inverse_logc4_curve(np.array([0.09285527796717754, 0.4090068696819821, 0.6577136499999999])), np.array([0.04345044, 0.18, 1.0])))


if __name__ == '__main__':
    unittest.main()
</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.<environment_details>
# VSCode Visible Files
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
pixelpasta/tests/test_color_analysis.py

# VSCode Open Tabs
pixelpasta/tests/test_cube_parser.py
pixelpasta/lut_processor/cube_parser.py
pixelpasta/app.py
pixelpasta/lut_processor/color_analysis.py
pixelpasta/templates/upload.html
pixelpasta/tests/test_color_analysis.py

# Current Time
19/03/2025, 6:47:05 pm (Europe/Warsaw, UTC+1:00)

# Current Mode
ACT MODE
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])))

    def test_inverse_slog3_curve(self):
        a = 0.432699
        b = 0.009468
        c = 0.655
        d = 0.037584
        e = 0.01
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), np.array([0.1])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), np.array([1.0])))
        self.assertTrue(np.allclose(inverse_slog3_curve(np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])), np.array([ (0.01 - e) / d, 0.1, 1.0])))

    def test_rec709_oetf(self):
        self.assertAlmostEqual(rec709_oetf(0.0), 0.0)
        self.assertAlmostEqual(rec709_oetf(0.018), 0.08124794403514046)
        self.assertAlmostEqual(rec709_oetf(1.0), 1.0)
        self.assertTrue(np.allclose(rec709_oetf(np.array([0.0, 0.018, 1.0])), np.array([0.0, 0.08124794403514046, 1.0])))

    def test_interpolate_1d_lut(self):
        lut_1d = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]])
        output = interpolate_1d_lut(lut_1d, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_interpolate_3d_lut(self):
        lut_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]
        ])
        lut_size = 2
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([
            [0.  , 0.  , 0.  ],
            [0.5 , 0.5 , 0.5 ],
            [1.  , 1.  , 1.  ]
        ])
        output = interpolate_3d_lut(lut_3d, lut_size, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_srgb_to_rec709(self):
        rgb_values = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        expected_output_sgamut3 = np.array([
            [ 1.641 , -0.6636,  0.0117],
            [-0.3245,  1.6157, -0.0085],
            [-0.3165,  0.0479,  0.9968]
        ])
        expected_output_sgamut3_cine = np.array([
            [ 1.5529, -0.5428, -0.0026],
            [-0.2555,  1.5027, -0.0186],
            [-0.2974,  0.0401,  1.0212]
        ])
        output_sgamut3 = srgb_to_rec709(rgb_values, 'S-Gamut3')
        output_sgamut3_cine = srgb_to_rec709(rgb_values, 'S-Gamut3.Cine')
        self.assertTrue(np.allclose(output_sgamut3, expected_output_sgamut3))
        self.assertTrue(np.allclose(output_sgamut3_cine, expected_output_sgamut3_cine))
        with self.assertRaises(ValueError):
            srgb_to_rec709(rgb_values, 'InvalidColorSpace')

    def test_generate_table(self):
        # Tworzymy tymczasowy plik .cube
        content = """
TITLE "Test LUT"
LUT_1D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as temp_file:
            temp_file.write(content.encode())
            filepath = temp_file.name

        # Testujemy dla S-Gamut3
        df_sgamut3 = generate_table(filepath, 'S-Gamut3')
        self.assertIsInstance(df_sgamut3, pd.DataFrame)
        self.assertEqual(len(df_sgamut3), 20)
        self.assertEqual(df_sgamut3['Color Space'][0], 'S-Gamut3')

        # Testujemy dla S-Gamut3.Cine
        df_sgamut3_cine = generate_table(filepath, 'S-Gamut3.Cine')
        self.assertIsInstance(df_sgamut3_cine, pd.DataFrame)
        self.assertEqual(len(df_sgamut3_cine), 20)
        self.assertEqual(df_sgamut3_cine['Color Space'][0], 'S-Gamut3.Cine')

        os.remove(filepath) # Usuwamy tymczasowy plik

    def test_logc4_curve(self):
      self.assertTrue(np.allclose(logc4_curve(0.0), np.array([-3852.359026659536])))
      self.assertAlmostEqual(logc4_curve(0.18), 0.4090068696819821)
      self.assertTrue(np.allclose(logc4_curve(np.array([0.0, 0.18, 1.0])), np.array([-3852.359026659536, 0.4090068696819821, 0.6577136499999999])))

    def test_inverse_logc4_curve(self):
      self.assertTrue(np.allclose(inverse_logc4_curve(0.09285527796717754), np.array([0.04345044])))
      self.assertTrue(np.allclose(inverse_logc4_curve(0.4090068696819821), np.array([0.18])))
      self.assertTrue(np.allclose(inverse_logc4_curve(np.array([0.09285527796717754, 0.4090068696819821, 0.6577136499999999])), np.array([0.04345044, 0.18, 1.0])))


if __name__ == '__main__':
    unittest.main()
</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.<environment_details>
# VSCode Visible Files
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
pixelpasta/tests/test_color_analysis.py

# VSCode Open Tabs
pixelpasta/tests/test_cube_parser.py
pixelpasta/lut_processor/cube_parser.py
pixelpasta/app.py
pixelpasta/lut_processor/color_analysis.py
pixelpasta/templates/upload.html
pixelpasta/tests/test_color_analysis.py

# Current Time
19/03/2025, 6:47:05 pm (Europe/Warsaw, UTC+1:00)

# Current Mode
ACT MODE
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])))

    def test_inverse_slog3_curve(self):
        a = 0.432699
        b = 0.009468
        c = 0.655
        d = 0.037584
        e = 0.01
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), np.array([0.1])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), np.array([1.0])))
        self.assertTrue(np.allclose(inverse_slog3_curve(np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])), np.array([ (0.01 - e) / d, 0.1, 1.0])))

    def test_rec709_oetf(self):
        self.assertAlmostEqual(rec709_oetf(0.0), 0.0)
        self.assertAlmostEqual(rec709_oetf(0.018), 0.08124794403514046)
        self.assertAlmostEqual(rec709_oetf(1.0), 1.0)
        self.assertTrue(np.allclose(rec709_oetf(np.array([0.0, 0.018, 1.0])), np.array([0.0, 0.08124794403514046, 1.0])))

    def test_interpolate_1d_lut(self):
        lut_1d = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]])
        output = interpolate_1d_lut(lut_1d, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_interpolate_3d_lut(self):
        lut_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]
        ])
        lut_size = 2
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([
            [0.  , 0.  , 0.  ],
            [0.5 , 0.5 , 0.5 ],
            [1.  , 1.  , 1.  ]
        ])
        output = interpolate_3d_lut(lut_3d, lut_size, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_srgb_to_rec709(self):
        rgb_values = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        expected_output_sgamut3 = np.array([
            [ 1.641 , -0.6636,  0.0117],
            [-0.3245,  1.6157, -0.0085],
            [-0.3165,  0.0479,  0.9968]
        ])
        expected_output_sgamut3_cine = np.array([
            [ 1.5529, -0.5428, -0.0026],
            [-0.2555,  1.5027, -0.0186],
            [-0.2974,  0.0401,  1.0212]
        ])
        output_sgamut3 = srgb_to_rec709(rgb_values, 'S-Gamut3')
        output_sgamut3_cine = srgb_to_rec709(rgb_values, 'S-Gamut3.Cine')
        self.assertTrue(np.allclose(output_sgamut3, expected_output_sgamut3))
        self.assertTrue(np.allclose(output_sgamut3_cine, expected_output_sgamut3_cine))
        with self.assertRaises(ValueError):
            srgb_to_rec709(rgb_values, 'InvalidColorSpace')

    def test_generate_table(self):
        # Tworzymy tymczasowy plik .cube
        content = """
TITLE "Test LUT"
LUT_1D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as temp_file:
            temp_file.write(content.encode())
            filepath = temp_file.name

        # Testujemy dla S-Gamut3
        df_sgamut3 = generate_table(filepath, 'S-Gamut3')
        self.assertIsInstance(df_sgamut3, pd.DataFrame)
        self.assertEqual(len(df_sgamut3), 20)
        self.assertEqual(df_sgamut3['Color Space'][0], 'S-Gamut3')

        # Testujemy dla S-Gamut3.Cine
        df_sgamut3_cine = generate_table(filepath, 'S-Gamut3.Cine')
        self.assertIsInstance(df_sgamut3_cine, pd.DataFrame)
        self.assertEqual(len(df_sgamut3_cine), 20)
        self.assertEqual(df_sgamut3_cine['Color Space'][0], 'S-Gamut3.Cine')

        os.remove(filepath) # Usuwamy tymczasowy plik

    def test_logc4_curve(self):
      self.assertTrue(np.allclose(logc4_curve(0.0), np.array([-3852.359026659536])))
      self.assertAlmostEqual(logc4_curve(0.18), 0.4090068696819821)
      self.assertTrue(np.allclose(logc4_curve(np.array([0.0, 0.18, 1.0])), np.array([-3852.359026659536, 0.4090068696819821, 0.6577136499999999])))

    def test_inverse_logc4_curve(self):
      self.assertTrue(np.allclose(inverse_logc4_curve(0.09285527796717754), np.array([0.04345044])))
      self.assertTrue(np.allclose(inverse_logc4_curve(0.4090068696819821), np.array([0.18])))
      self.assertTrue(np.allclose(inverse_logc4_curve(np.array([0.09285527796717754, 0.4090068696819821, 0.6577136499999999])), np.array([0.04345044, 0.18, 1.0])))


if __name__ == '__main__':
    unittest.main()
</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.<environment_details>
# VSCode Visible Files
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
pixelpasta/tests/test_color_analysis.py

# VSCode Open Tabs
pixelpasta/tests/test_cube_parser.py
pixelpasta/lut_processor/cube_parser.py
pixelpasta/app.py
pixelpasta/lut_processor/color_analysis.py
pixelpasta/templates/upload.html
pixelpasta/tests/test_color_analysis.py

# Current Time
19/03/2025, 6:47:05 pm (Europe/Warsaw, UTC+1:00)

# Current Mode
ACT MODE
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 +
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])))

    def test_inverse_slog3_curve(self):
        a = 0.432699
        b = 0.009468
        c = 0.655
        d = 0.037584
        e = 0.01
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), np.array([0.1])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), np.array([1.0])))
        self.assertTrue(np.allclose(inverse_slog3_curve(np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])), np.array([ (0.01 - e) / d, 0.1, 1.0])))

    def test_rec709_oetf(self):
        self.assertAlmostEqual(rec709_oetf(0.0), 0.0)
        self.assertAlmostEqual(rec709_oetf(0.018), 0.08124794403514046)
        self.assertAlmostEqual(rec709_oetf(1.0), 1.0)
        self.assertTrue(np.allclose(rec709_oetf(np.array([0.0, 0.018, 1.0])), np.array([0.0, 0.08124794403514046, 1.0])))

    def test_interpolate_1d_lut(self):
        lut_1d = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]])
        output = interpolate_1d_lut(lut_1d, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_interpolate_3d_lut(self):
        lut_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]
        ])
        lut_size = 2
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([
            [0.  , 0.  , 0.  ],
            [0.5 , 0.5 , 0.5 ],
            [1.  , 1.  , 1.  ]
        ])
        output = interpolate_3d_lut(lut_3d, lut_size, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_srgb_to_rec709(self):
        rgb_values = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        expected_output_sgamut3 = np.array([
            [ 1.641 , -0.6636,  0.0117],
            [-0.3245,  1.6157, -0.0085],
            [-0.3165,  0.0479,  0.9968]
        ])
        expected_output_sgamut3_cine = np.array([
            [ 1.5529, -0.5428, -0.0026],
            [-0.2555,  1.5027, -0.0186],
            [-0.2974,  0.0401,  1.0212]
        ])
        output_sgamut3 = srgb_to_rec709(rgb_values, 'S-Gamut3')
        output_sgamut3_cine = srgb_to_rec709(rgb_values, 'S-Gamut3.Cine')
        self.assertTrue(np.allclose(output_sgamut3, expected_output_sgamut3))
        self.assertTrue(np.allclose(output_sgamut3_cine, expected_output_sgamut3_cine))
        with self.assertRaises(ValueError):
            srgb_to_rec709(rgb_values, 'InvalidColorSpace')

    def test_generate_table(self):
        # Tworzymy tymczasowy plik .cube
        content = """
TITLE "Test LUT"
LUT_1D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as temp_file:
            temp_file.write(content.encode())
            filepath = temp_file.name

        # Testujemy dla S-Gamut3
        df_sgamut3 = generate_table(filepath, 'S-Gamut3')
        self.assertIsInstance(df_sgamut3, pd.DataFrame)
        self.assertEqual(len(df_sgamut3), 20)
        self.assertEqual(df_sgamut3['Color Space'][0], 'S-Gamut3')

        # Testujemy dla S-Gamut3.Cine
        df_sgamut3_cine = generate_table(filepath, 'S-Gamut3.Cine')
        self.assertIsInstance(df_sgamut3_cine, pd.DataFrame)
        self.assertEqual(len(df_sgamut3_cine), 20)
        self.assertEqual(df_sgamut3_cine['Color Space'][0], 'S-Gamut3.Cine')

        os.remove(filepath) # Usuwamy tymczasowy plik

    def test_logc4_curve(self):
      self.assertTrue(np.allclose(logc4_curve(0.0), np.array([-3852.359026659536])))
      self.assertAlmostEqual(logc4_curve(0.18), 0.4090068696819821)
      self.assertTrue(np.allclose(logc4_curve(np.array([0.0, 0.18, 1.0])), np.array([-3852.359026659536, 0.4090068696819821, 0.6577136499999999])))

    def test_inverse_logc4_curve(self):
      self.assertTrue(np.allclose(inverse_logc4_curve(0.09285527796717754), np.array([0.04345044])))
      self.assertTrue(np.allclose(inverse_logc4_curve(0.4090068696819821), np.array([0.18])))
      self.assertTrue(np.allclose(inverse_logc4_curve(np.array([0.09285527796717754, 0.4090068696819821, 0.6577136499999999])), np.array([0.04345044, 0.18, 1.0])))


if __name__ == '__main__':
    unittest.main()
</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.<environment_details>
# VSCode Visible Files
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
pixelpasta/tests/test_color_analysis.py

# VSCode Open Tabs
pixelpasta/tests/test_cube_parser.py
pixelpasta/lut_processor/cube_parser.py
pixelpasta/app.py
pixelpasta/lut_processor/color_analysis.py
pixelpasta/templates/upload.html
pixelpasta/tests/test_color_analysis.py

# Current Time
19/03/2025, 6:47:05 pm (Europe/Warsaw, UTC+1:00)

# Current Mode
ACT MODE
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])))

    def test_inverse_slog3_curve(self):
        a = 0.432699
        b = 0.009468
        c = 0.655
        d = 0.037584
        e = 0.01
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), np.array([0.1])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), np.array([1.0])))
        self.assertTrue(np.allclose(inverse_slog3_curve(np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])), np.array([ (0.01 - e) / d, 0.1, 1.0])))

    def test_rec709_oetf(self):
        self.assertAlmostEqual(rec709_oetf(0.0), 0.0)
        self.assertAlmostEqual(rec709_oetf(0.018), 0.08124794403514046)
        self.assertAlmostEqual(rec709_oetf(1.0), 1.0)
        self.assertTrue(np.allclose(rec709_oetf(np.array([0.0, 0.018, 1.0])), np.array([0.0, 0.08124794403514046, 1.0])))

    def test_interpolate_1d_lut(self):
        lut_1d = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]])
        output = interpolate_1d_lut(lut_1d, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_interpolate_3d_lut(self):
        lut_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]
        ])
        lut_size = 2
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([
            [0.  , 0.  , 0.  ],
            [0.5 , 0.5 , 0.5 ],
            [1.  , 1.  , 1.  ]
        ])
        output = interpolate_3d_lut(lut_3d, lut_size, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_srgb_to_rec709(self):
        rgb_values = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        expected_output_sgamut3 = np.array([
            [ 1.641 , -0.6636,  0.0117],
            [-0.3245,  1.6157, -0.0085],
            [-0.3165,  0.0479,  0.9968]
        ])
        expected_output_sgamut3_cine = np.array([
            [ 1.5529, -0.5428, -0.0026],
            [-0.2555,  1.5027, -0.0186],
            [-0.2974,  0.0401,  1.0212]
        ])
        output_sgamut3 = srgb_to_rec709(rgb_values, 'S-Gamut3')
        output_sgamut3_cine = srgb_to_rec709(rgb_values, 'S-Gamut3.Cine')
        self.assertTrue(np.allclose(output_sgamut3, expected_output_sgamut3))
        self.assertTrue(np.allclose(output_sgamut3_cine, expected_output_sgamut3_cine))
        with self.assertRaises(ValueError):
            srgb_to_rec709(rgb_values, 'InvalidColorSpace')

    def test_generate_table(self):
        # Tworzymy tymczasowy plik .cube
        content = """
TITLE "Test LUT"
LUT_1D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as temp_file:
            temp_file.write(content.encode())
            filepath = temp_file.name

        # Testujemy dla S-Gamut3
        df_sgamut3 = generate_table(filepath, 'S-Gamut3')
        self.assertIsInstance(df_sgamut3, pd.DataFrame)
        self.assertEqual(len(df_sgamut3), 20)
        self.assertEqual(df_sgamut3['Color Space'][0], 'S-Gamut3')

        # Testujemy dla S-Gamut3.Cine
        df_sgamut3_cine = generate_table(filepath, 'S-Gamut3.Cine')
        self.assertIsInstance(df_sgamut3_cine, pd.DataFrame)
        self.assertEqual(len(df_sgamut3_cine), 20)
        self.assertEqual(df_sgamut3_cine['Color Space'][0], 'S-Gamut3.Cine')

        os.remove(filepath) # Usuwamy tymczasowy plik

    def test_logc4_curve(self):
      self.assertTrue(np.allclose(logc4_curve(0.0), np.array([-3852.359026659536])))
      self.assertAlmostEqual(logc4_curve(0.18), 0.4090068696819821)
      self.assertTrue(np.allclose(logc4_curve(np.array([0.0, 0.18, 1.0])), np.array([-3852.359026659536, 0.4090068696819821, 0.6577136499999999])))

    def test_inverse_logc4_curve(self):
      self.assertTrue(np.allclose(inverse_logc4_curve(0.09285527796717754), np.array([0.04345044])))
      self.assertTrue(np.allclose(inverse_logc4_curve(0.4090068696819821), np.array([0.18])))
      self.assertTrue(np.allclose(inverse_logc4_curve(np.array([0.09285527796717754, 0.4090068696819821, 0.6577136499999999])), np.array([0.04345044, 0.18, 1.0])))


if __name__ == '__main__':
    unittest.main()
</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.<environment_details>
# VSCode Visible Files
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
pixelpasta/tests/test_color_analysis.py

# VSCode Open Tabs
pixelpasta/tests/test_cube_parser.py
pixelpasta/lut_processor/cube_parser.py
pixelpasta/app.py
pixelpasta/lut_processor/color_analysis.py
pixelpasta/templates/upload.html
pixelpasta/tests/test_color_analysis.py

# Current Time
19/03/2025, 6:47:05 pm (Europe/Warsaw, UTC+1:00)

# Current Mode
ACT MODE
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])))

    def test_inverse_slog3_curve(self):
        a = 0.432699
        b = 0.009468
        c = 0.655
        d = 0.037584
        e = 0.01
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), np.array([0.1])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), np.array([1.0])))
        self.assertTrue(np.allclose(inverse_slog3_curve(np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])), np.array([ (0.01 - e) / d, 0.1, 1.0])))

    def test_rec709_oetf(self):
        self.assertAlmostEqual(rec709_oetf(0.0), 0.0)
        self.assertAlmostEqual(rec709_oetf(0.018), 0.08124794403514046)
        self.assertAlmostEqual(rec709_oetf(1.0), 1.0)
        self.assertTrue(np.allclose(rec709_oetf(np.array([0.0, 0.018, 1.0])), np.array([0.0, 0.08124794403514046, 1.0])))

    def test_interpolate_1d_lut(self):
        lut_1d = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]])
        output = interpolate_1d_lut(lut_1d, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_interpolate_3d_lut(self):
        lut_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]
        ])
        lut_size = 2
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([
            [0.  , 0.  , 0.  ],
            [0.5 , 0.5 , 0.5 ],
            [1.  , 1.  , 1.  ]
        ])
        output = interpolate_3d_lut(lut_3d, lut_size, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_srgb_to_rec709(self):
        rgb_values = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        expected_output_sgamut3 = np.array([
            [ 1.641 , -0.6636,  0.0117],
            [-0.3245,  1.6157, -0.0085],
            [-0.3165,  0.0479,  0.9968]
        ])
        expected_output_sgamut3_cine = np.array([
            [ 1.5529, -0.5428, -0.0026],
            [-0.2555,  1.5027, -0.0186],
            [-0.2974,  0.0401,  1.0212]
        ])
        output_sgamut3 = srgb_to_rec709(rgb_values, 'S-Gamut3')
        output_sgamut3_cine = srgb_to_rec709(rgb_values, 'S-Gamut3.Cine')
        self.assertTrue(np.allclose(output_sgamut3, expected_output_sgamut3))
        self.assertTrue(np.allclose(output_sgamut3_cine, expected_output_sgamut3_cine))
        with self.assertRaises(ValueError):
            srgb_to_rec709(rgb_values, 'InvalidColorSpace')

    def test_generate_table(self):
        # Tworzymy tymczasowy plik .cube
        content = """
TITLE "Test LUT"
LUT_1D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as temp_file:
            temp_file.write(content.encode())
            filepath = temp_file.name

        # Testujemy dla S-Gamut3
        df_sgamut3 = generate_table(filepath, 'S-Gamut3')
        self.assertIsInstance(df_sgamut3, pd.DataFrame)
        self.assertEqual(len(df_sgamut3), 20)
        self.assertEqual(df_sgamut3['Color Space'][0], 'S-Gamut3')

        # Testujemy dla S-Gamut3.Cine
        df_sgamut3_cine = generate_table(filepath, 'S-Gamut3.Cine')
        self.assertIsInstance(df_sgamut3_cine, pd.DataFrame)
        self.assertEqual(len(df_sgamut3_cine), 20)
        self.assertEqual(df_sgamut3_cine['Color Space'][0], 'S-Gamut3.Cine')

        os.remove(filepath) # Usuwamy tymczasowy plik

    def test_logc4_curve(self):
      self.assertTrue(np.allclose(logc4_curve(0.0), np.array([-3852.359026659536])))
      self.assertAlmostEqual(logc4_curve(0.18), 0.4090068696819821)
      self.assertTrue(np.allclose(logc4_curve(np.array([0.0, 0.18, 1.0])), np.array([-3852.359026659536, 0.4090068696819821, 0.6577136499999999])))

    def test_inverse_logc4_curve(self):
      self.assertTrue(np.allclose(inverse_logc4_curve(0.09285527796717754), np.array([0.04345044])))
      self.assertTrue(np.allclose(inverse_logc4_curve(0.4090068696819821), np.array([0.18])))
      self.assertTrue(np.allclose(inverse_logc4_curve(np.array([0.09285527796717754, 0.4090068696819821, 0.6577136499999999])), np.array([0.04345044, 0.18, 1.0])))


if __name__ == '__main__':
    unittest.main()
</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.<environment_details>
# VSCode Visible Files
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
pixelpasta/tests/test_color_analysis.py

# VSCode Open Tabs
pixelpasta/tests/test_cube_parser.py
pixelpasta/lut_processor/cube_parser.py
pixelpasta/app.py
pixelpasta/lut_processor/color_analysis.py
pixelpasta/templates/upload.html
pixelpasta/tests/test_color_analysis.py

# Current Time
19/03/2025, 6:47:05 pm (Europe/Warsaw, UTC+1:00)

# Current Mode
ACT MODE
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])))

    def test_inverse_slog3_curve(self):
        a = 0.432699
        b = 0.009468
        c = 0.655
        d = 0.037584
        e = 0.01
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), np.array([0.1])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), np.array([1.0])))
        self.assertTrue(np.allclose(inverse_slog3_curve(np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])), np.array([ (0.01 - e) / d, 0.1, 1.0])))

    def test_rec709_oetf(self):
        self.assertAlmostEqual(rec709_oetf(0.0), 0.0)
        self.assertAlmostEqual(rec709_oetf(0.018), 0.08124794403514046)
        self.assertAlmostEqual(rec709_oetf(1.0), 1.0)
        self.assertTrue(np.allclose(rec709_oetf(np.array([0.0, 0.018, 1.0])), np.array([0.0, 0.08124794403514046, 1.0])))

    def test_interpolate_1d_lut(self):
        lut_1d = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]])
        output = interpolate_1d_lut(lut_1d, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_interpolate_3d_lut(self):
        lut_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]
        ])
        lut_size = 2
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([
            [0.  , 0.  , 0.  ],
            [0.5 , 0.5 , 0.5 ],
            [1.  , 1.  , 1.  ]
        ])
        output = interpolate_3d_lut(lut_3d, lut_size, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_srgb_to_rec709(self):
        rgb_values = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        expected_output_sgamut3 = np.array([
            [ 1.641 , -0.6636,  0.0117],
            [-0.3245,  1.6157, -0.0085],
            [-0.3165,  0.0479,  0.9968]
        ])
        expected_output_sgamut3_cine = np.array([
            [ 1.5529, -0.5428, -0.0026],
            [-0.2555,  1.5027, -0.0186],
            [-0.2974,  0.0401,  1.0212]
        ])
        output_sgamut3 = srgb_to_rec709(rgb_values, 'S-Gamut3')
        output_sgamut3_cine = srgb_to_rec709(rgb_values, 'S-Gamut3.Cine')
        self.assertTrue(np.allclose(output_sgamut3, expected_output_sgamut3))
        self.assertTrue(np.allclose(output_sgamut3_cine, expected_output_sgamut3_cine))
        with self.assertRaises(ValueError):
            srgb_to_rec709(rgb_values, 'InvalidColorSpace')

    def test_generate_table(self):
        # Tworzymy tymczasowy plik .cube
        content = """
TITLE "Test LUT"
LUT_1D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as temp_file:
            temp_file.write(content.encode())
            filepath = temp_file.name

        # Testujemy dla S-Gamut3
        df_sgamut3 = generate_table(filepath, 'S-Gamut3')
        self.assertIsInstance(df_sgamut3, pd.DataFrame)
        self.assertEqual(len(df_sgamut3), 20)
        self.assertEqual(df_sgamut3['Color Space'][0], 'S-Gamut3')

        # Testujemy dla S-Gamut3.Cine
        df_sgamut3_cine = generate_table(filepath, 'S-Gamut3.Cine')
        self.assertIsInstance(df_sgamut3_cine, pd.DataFrame)
        self.assertEqual(len(df_sgamut3_cine), 20)
        self.assertEqual(df_sgamut3_cine['Color Space'][0], 'S-Gamut3.Cine')

        os.remove(filepath) # Usuwamy tymczasowy plik

    def test_logc4_curve(self):
      self.assertTrue(np.allclose(logc4_curve(0.0), np.array([-3852.359026659536])))
      self.assertAlmostEqual(logc4_curve(0.18), 0.4090068696819821)
      self.assertTrue(np.allclose(logc4_curve(np.array([0.0, 0.18, 1.0])), np.array([-3852.359026659536, 0.4090068696819821, 0.6577136499999999])))

    def test_inverse_logc4_curve(self):
      self.assertTrue(np.allclose(inverse_logc4_curve(0.09285527796717754), np.array([0.04345044])))
      self.assertTrue(np.allclose(inverse_logc4_curve(0.4090068696819821), np.array([0.18])))
      self.assertTrue(np.allclose(inverse_logc4_curve(np.array([0.09285527796717754, 0.4090068696819821, 0.6577136499999999])), np.array([0.04345044, 0.18, 1.0])))


if __name__ == '__main__':
    unittest.main()
</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.<environment_details>
# VSCode Visible Files
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
pixelpasta/tests/test_color_analysis.py

# VSCode Open Tabs
pixelpasta/tests/test_cube_parser.py
pixelpasta/lut_processor/cube_parser.py
pixelpasta/app.py
pixelpasta/lut_processor/color_analysis.py
pixelpasta/templates/upload.html
pixelpasta/tests/test_color_analysis.py

# Current Time
19/03/2025, 6:47:05 pm (Europe/Warsaw, UTC+1:00)

# Current Mode
ACT MODE
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 +
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])))

    def test_inverse_slog3_curve(self):
        a = 0.432699
        b = 0.009468
        c = 0.655
        d = 0.037584
        e = 0.01
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), np.array([0.1])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), np.array([1.0])))
        self.assertTrue(np.allclose(inverse_slog3_curve(np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])), np.array([ (0.01 - e) / d, 0.1, 1.0])))

    def test_rec709_oetf(self):
        self.assertAlmostEqual(rec709_oetf(0.0), 0.0)
        self.assertAlmostEqual(rec709_oetf(0.018), 0.08124794403514046)
        self.assertAlmostEqual(rec709_oetf(1.0), 1.0)
        self.assertTrue(np.allclose(rec709_oetf(np.array([0.0, 0.018, 1.0])), np.array([0.0, 0.08124794403514046, 1.0])))

    def test_interpolate_1d_lut(self):
        lut_1d = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]])
        output = interpolate_1d_lut(lut_1d, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_interpolate_3d_lut(self):
        lut_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]
        ])
        lut_size = 2
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([
            [0.  , 0.  , 0.  ],
            [0.5 , 0.5 , 0.5 ],
            [1.  , 1.  , 1.  ]
        ])
        output = interpolate_3d_lut(lut_3d, lut_size, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_srgb_to_rec709(self):
        rgb_values = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        expected_output_sgamut3 = np.array([
            [ 1.641 , -0.6636,  0.0117],
            [-0.3245,  1.6157, -0.0085],
            [-0.3165,  0.0479,  0.9968]
        ])
        expected_output_sgamut3_cine = np.array([
            [ 1.5529, -0.5428, -0.0026],
            [-0.2555,  1.5027, -0.0186],
            [-0.2974,  0.0401,  1.0212]
        ])
        output_sgamut3 = srgb_to_rec709(rgb_values, 'S-Gamut3')
        output_sgamut3_cine = srgb_to_rec709(rgb_values, 'S-Gamut3.Cine')
        self.assertTrue(np.allclose(output_sgamut3, expected_output_sgamut3))
        self.assertTrue(np.allclose(output_sgamut3_cine, expected_output_sgamut3_cine))
        with self.assertRaises(ValueError):
            srgb_to_rec709(rgb_values, 'InvalidColorSpace')

    def test_generate_table(self):
        # Tworzymy tymczasowy plik .cube
        content = """
TITLE "Test LUT"
LUT_1D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as temp_file:
            temp_file.write(content.encode())
            filepath = temp_file.name

        # Testujemy dla S-Gamut3
        df_sgamut3 = generate_table(filepath, 'S-Gamut3')
        self.assertIsInstance(df_sgamut3, pd.DataFrame)
        self.assertEqual(len(df_sgamut3), 20)
        self.assertEqual(df_sgamut3['Color Space'][0], 'S-Gamut3')

        # Testujemy dla S-Gamut3.Cine
        df_sgamut3_cine = generate_table(filepath, 'S-Gamut3.Cine')
        self.assertIsInstance(df_sgamut3_cine, pd.DataFrame)
        self.assertEqual(len(df_sgamut3_cine), 20)
        self.assertEqual(df_sgamut3_cine['Color Space'][0], 'S-Gamut3.Cine')

        os.remove(filepath) # Usuwamy tymczasowy plik

    def test_logc4_curve(self):
      self.assertTrue(np.allclose(logc4_curve(0.0), np.array([-3852.359026659536])))
      self.assertAlmostEqual(logc4_curve(0.18), 0.4090068696819821)
      self.assertTrue(np.allclose(logc4_curve(np.array([0.0, 0.18, 1.0])), np.array([-3852.359026659536, 0.4090068696819821, 0.6577136499999999])))

    def test_inverse_logc4_curve(self):
      self.assertTrue(np.allclose(inverse_logc4_curve(0.09285527796717754), np.array([0.04345044])))
      self.assertTrue(np.allclose(inverse_logc4_curve(0.4090068696819821), np.array([0.18])))
      self.assertTrue(np.allclose(inverse_logc4_curve(np.array([0.09285527796717754, 0.4090068696819821, 0.6577136499999999])), np.array([0.04345044, 0.18, 1.0])))


if __name__ == '__main__':
    unittest.main()
</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.<environment_details>
# VSCode Visible Files
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
pixelpasta/tests/test_color_analysis.py

# VSCode Open Tabs
pixelpasta/tests/test_cube_parser.py
pixelpasta/lut_processor/cube_parser.py
pixelpasta/app.py
pixelpasta/lut_processor/color_analysis.py
pixelpasta/templates/upload.html
pixelpasta/tests/test_color_analysis.py

# Current Time
19/03/2025, 6:47:05 pm (Europe/Warsaw, UTC+1:00)

# Current Mode
ACT MODE
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])))

    def test_inverse_slog3_curve(self):
        a = 0.432699
        b = 0.009468
        c = 0.655
        d = 0.037584
        e = 0.01
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), np.array([0.1])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), np.array([1.0])))
        self.assertTrue(np.allclose(inverse_slog3_curve(np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])), np.array([ (0.01 - e) / d, 0.1, 1.0])))

    def test_rec709_oetf(self):
        self.assertAlmostEqual(rec709_oetf(0.0), 0.0)
        self.assertAlmostEqual(rec709_oetf(0.018), 0.08124794403514046)
        self.assertAlmostEqual(rec709_oetf(1.0), 1.0)
        self.assertTrue(np.allclose(rec709_oetf(np.array([0.0, 0.018, 1.0])), np.array([0.0, 0.08124794403514046, 1.0])))

    def test_interpolate_1d_lut(self):
        lut_1d = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]])
        output = interpolate_1d_lut(lut_1d, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_interpolate_3d_lut(self):
        lut_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]
        ])
        lut_size = 2
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([
            [0.  , 0.  , 0.  ],
            [0.5 , 0.5 , 0.5 ],
            [1.  , 1.  , 1.  ]
        ])
        output = interpolate_3d_lut(lut_3d, lut_size, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_srgb_to_rec709(self):
        rgb_values = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        expected_output_sgamut3 = np.array([
            [ 1.641 , -0.6636,  0.0117],
            [-0.3245,  1.6157, -0.0085],
            [-0.3165,  0.0479,  0.9968]
        ])
        expected_output_sgamut3_cine = np.array([
            [ 1.5529, -0.5428, -0.0026],
            [-0.2555,  1.5027, -0.0186],
            [-0.2974,  0.0401,  1.0212]
        ])
        output_sgamut3 = srgb_to_rec709(rgb_values, 'S-Gamut3')
        output_sgamut3_cine = srgb_to_rec709(rgb_values, 'S-Gamut3.Cine')
        self.assertTrue(np.allclose(output_sgamut3, expected_output_sgamut3))
        self.assertTrue(np.allclose(output_sgamut3_cine, expected_output_sgamut3_cine))
        with self.assertRaises(ValueError):
            srgb_to_rec709(rgb_values, 'InvalidColorSpace')

    def test_generate_table(self):
        # Tworzymy tymczasowy plik .cube
        content = """
TITLE "Test LUT"
LUT_1D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as temp_file:
            temp_file.write(content.encode())
            filepath = temp_file.name

        # Testujemy dla S-Gamut3
        df_sgamut3 = generate_table(filepath, 'S-Gamut3')
        self.assertIsInstance(df_sgamut3, pd.DataFrame)
        self.assertEqual(len(df_sgamut3), 20)
        self.assertEqual(df_sgamut3['Color Space'][0], 'S-Gamut3')

        # Testujemy dla S-Gamut3.Cine
        df_sgamut3_cine = generate_table(filepath, 'S-Gamut3.Cine')
        self.assertIsInstance(df_sgamut3_cine, pd.DataFrame)
        self.assertEqual(len(df_sgamut3_cine), 20)
        self.assertEqual(df_sgamut3_cine['Color Space'][0], 'S-Gamut3.Cine')

        os.remove(filepath) # Usuwamy tymczasowy plik

    def test_logc4_curve(self):
      self.assertTrue(np.allclose(logc4_curve(0.0), np.array([-3852.359026659536])))
      self.assertAlmostEqual(logc4_curve(0.18), 0.4090068696819821)
      self.assertTrue(np.allclose(logc4_curve(np.array([0.0, 0.18, 1.0])), np.array([-3852.359026659536, 0.4090068696819821, 0.6577136499999999])))

    def test_inverse_logc4_curve(self):
      self.assertTrue(np.allclose(inverse_logc4_curve(0.09285527796717754), np.array([0.04345044])))
      self.assertTrue(np.allclose(inverse_logc4_curve(0.4090068696819821), np.array([0.18])))
      self.assertTrue(np.allclose(inverse_logc4_curve(np.array([0.09285527796717754, 0.4090068696819821, 0.6577136499999999])), np.array([0.04345044, 0.18, 1.0])))


if __name__ == '__main__':
    unittest.main()
</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.<environment_details>
# VSCode Visible Files
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
pixelpasta/tests/test_color_analysis.py

# VSCode Open Tabs
pixelpasta/tests/test_cube_parser.py
pixelpasta/lut_processor/cube_parser.py
pixelpasta/app.py
pixelpasta/lut_processor/color_analysis.py
pixelpasta/templates/upload.html
pixelpasta/tests/test_color_analysis.py

# Current Time
19/03/2025, 6:47:05 pm (Europe/Warsaw, UTC+1:00)

# Current Mode
ACT MODE
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])))

    def test_inverse_slog3_curve(self):
        a = 0.432699
        b = 0.009468
        c = 0.655
        d = 0.037584
        e = 0.01
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), np.array([0.1])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), np.array([1.0])))
        self.assertTrue(np.allclose(inverse_slog3_curve(np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])), np.array([ (0.01 - e) / d, 0.1, 1.0])))

    def test_rec709_oetf(self):
        self.assertAlmostEqual(rec709_oetf(0.0), 0.0)
        self.assertAlmostEqual(rec709_oetf(0.018), 0.08124794403514046)
        self.assertAlmostEqual(rec709_oetf(1.0), 1.0)
        self.assertTrue(np.allclose(rec709_oetf(np.array([0.0, 0.018, 1.0])), np.array([0.0, 0.08124794403514046, 1.0])))

    def test_interpolate_1d_lut(self):
        lut_1d = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]])
        output = interpolate_1d_lut(lut_1d, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_interpolate_3d_lut(self):
        lut_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]
        ])
        lut_size = 2
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([
            [0.  , 0.  , 0.  ],
            [0.5 , 0.5 , 0.5 ],
            [1.  , 1.  , 1.  ]
        ])
        output = interpolate_3d_lut(lut_3d, lut_size, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_srgb_to_rec709(self):
        rgb_values = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        expected_output_sgamut3 = np.array([
            [ 1.641 , -0.6636,  0.0117],
            [-0.3245,  1.6157, -0.0085],
            [-0.3165,  0.0479,  0.9968]
        ])
        expected_output_sgamut3_cine = np.array([
            [ 1.5529, -0.5428, -0.0026],
            [-0.2555,  1.5027, -0.0186],
            [-0.2974,  0.0401,  1.0212]
        ])
        output_sgamut3 = srgb_to_rec709(rgb_values, 'S-Gamut3')
        output_sgamut3_cine = srgb_to_rec709(rgb_values, 'S-Gamut3.Cine')
        self.assertTrue(np.allclose(output_sgamut3, expected_output_sgamut3))
        self.assertTrue(np.allclose(output_sgamut3_cine, expected_output_sgamut3_cine))
        with self.assertRaises(ValueError):
            srgb_to_rec709(rgb_values, 'InvalidColorSpace')

    def test_generate_table(self):
        # Tworzymy tymczasowy plik .cube
        content = """
TITLE "Test LUT"
LUT_1D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as temp_file:
            temp_file.write(content.encode())
            filepath = temp_file.name

        # Testujemy dla S-Gamut3
        df_sgamut3 = generate_table(filepath, 'S-Gamut3')
        self.assertIsInstance(df_sgamut3, pd.DataFrame)
        self.assertEqual(len(df_sgamut3), 20)
        self.assertEqual(df_sgamut3['Color Space'][0], 'S-Gamut3')

        # Testujemy dla S-Gamut3.Cine
        df_sgamut3_cine = generate_table(filepath, 'S-Gamut3.Cine')
        self.assertIsInstance(df_sgamut3_cine, pd.DataFrame)
        self.assertEqual(len(df_sgamut3_cine), 20)
        self.assertEqual(df_sgamut3_cine['Color Space'][0], 'S-Gamut3.Cine')

        os.remove(filepath) # Usuwamy tymczasowy plik

    def test_logc4_curve(self):
      self.assertTrue(np.allclose(logc4_curve(0.0), np.array([-3852.359026659536])))
      self.assertAlmostEqual(logc4_curve(0.18), 0.4090068696819821)
      self.assertTrue(np.allclose(logc4_curve(np.array([0.0, 0.18, 1.0])), np.array([-3852.359026659536, 0.4090068696819821, 0.6577136499999999])))

    def test_inverse_logc4_curve(self):
      self.assertTrue(np.allclose(inverse_logc4_curve(0.09285527796717754), np.array([0.04345044])))
      self.assertTrue(np.allclose(inverse_logc4_curve(0.4090068696819821), np.array([0.18])))
      self.assertTrue(np.allclose(inverse_logc4_curve(np.array([0.09285527796717754, 0.4090068696819821, 0.6577136499999999])), np.array([0.04345044, 0.18, 1.0])))


if __name__ == '__main__':
    unittest.main()
</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.<environment_details>
# VSCode Visible Files
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
pixelpasta/tests/test_color_analysis.py

# VSCode Open Tabs
pixelpasta/tests/test_cube_parser.py
pixelpasta/lut_processor/cube_parser.py
pixelpasta/app.py
pixelpasta/lut_processor/color_analysis.py
pixelpasta/templates/upload.html
pixelpasta/tests/test_color_analysis.py

# Current Time
19/03/2025, 6:47:05 pm (Europe/Warsaw, UTC+1:00)

# Current Mode
ACT MODE
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])))

    def test_inverse_slog3_curve(self):
        a = 0.432699
        b = 0.009468
        c = 0.655
        d = 0.037584
        e = 0.01
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), np.array([0.1])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), np.array([1.0])))
        self.assertTrue(np.allclose(inverse_slog3_curve(np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])), np.array([ (0.01 - e) / d, 0.1, 1.0])))

    def test_rec709_oetf(self):
        self.assertAlmostEqual(rec709_oetf(0.0), 0.0)
        self.assertAlmostEqual(rec709_oetf(0.018), 0.08124794403514046)
        self.assertAlmostEqual(rec709_oetf(1.0), 1.0)
        self.assertTrue(np.allclose(rec709_oetf(np.array([0.0, 0.018, 1.0])), np.array([0.0, 0.08124794403514046, 1.0])))

    def test_interpolate_1d_lut(self):
        lut_1d = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]])
        output = interpolate_1d_lut(lut_1d, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_interpolate_3d_lut(self):
        lut_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]
        ])
        lut_size = 2
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([
            [0.  , 0.  , 0.  ],
            [0.5 , 0.5 , 0.5 ],
            [1.  , 1.  , 1.  ]
        ])
        output = interpolate_3d_lut(lut_3d, lut_size, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_srgb_to_rec709(self):
        rgb_values = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        expected_output_sgamut3 = np.array([
            [ 1.641 , -0.6636,  0.0117],
            [-0.3245,  1.6157, -0.0085],
            [-0.3165,  0.0479,  0.9968]
        ])
        expected_output_sgamut3_cine = np.array([
            [ 1.5529, -0.5428, -0.0026],
            [-0.2555,  1.5027, -0.0186],
            [-0.2974,  0.0401,  1.0212]
        ])
        output_sgamut3 = srgb_to_rec709(rgb_values, 'S-Gamut3')
        output_sgamut3_cine = srgb_to_rec709(rgb_values, 'S-Gamut3.Cine')
        self.assertTrue(np.allclose(output_sgamut3, expected_output_sgamut3))
        self.assertTrue(np.allclose(output_sgamut3_cine, expected_output_sgamut3_cine))
        with self.assertRaises(ValueError):
            srgb_to_rec709(rgb_values, 'InvalidColorSpace')

    def test_generate_table(self):
        # Tworzymy tymczasowy plik .cube
        content = """
TITLE "Test LUT"
LUT_1D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as temp_file:
            temp_file.write(content.encode())
            filepath = temp_file.name

        # Testujemy dla S-Gamut3
        df_sgamut3 = generate_table(filepath, 'S-Gamut3')
        self.assertIsInstance(df_sgamut3, pd.DataFrame)
        self.assertEqual(len(df_sgamut3), 20)
        self.assertEqual(df_sgamut3['Color Space'][0], 'S-Gamut3')

        # Testujemy dla S-Gamut3.Cine
        df_sgamut3_cine = generate_table(filepath, 'S-Gamut3.Cine')
        self.assertIsInstance(df_sgamut3_cine, pd.DataFrame)
        self.assertEqual(len(df_sgamut3_cine), 20)
        self.assertEqual(df_sgamut3_cine['Color Space'][0], 'S-Gamut3.Cine')

        os.remove(filepath) # Usuwamy tymczasowy plik

    def test_logc4_curve(self):
      self.assertTrue(np.allclose(logc4_curve(0.0), np.array([-3852.359026659536])))
      self.assertAlmostEqual(logc4_curve(0.18), 0.4090068696819821)
      self.assertTrue(np.allclose(logc4_curve(np.array([0.0, 0.18, 1.0])), np.array([-3852.359026659536, 0.4090068696819821, 0.6577136499999999])))

    def test_inverse_logc4_curve(self):
      self.assertTrue(np.allclose(inverse_logc4_curve(0.09285527796717754), np.array([0.04345044])))
      self.assertTrue(np.allclose(inverse_logc4_curve(0.4090068696819821), np.array([0.18])))
      self.assertTrue(np.allclose(inverse_logc4_curve(np.array([0.09285527796717754, 0.4090068696819821, 0.6577136499999999])), np.array([0.04345044, 0.18, 1.0])))


if __name__ == '__main__':
    unittest.main()
</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.<environment_details>
# VSCode Visible Files
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
../../../response_9b8d7021-0252-47d0-a858-70727aef6125/0
pixelpasta/tests/test_color_analysis.py

# VSCode Open Tabs
pixelpasta/tests/test_cube_parser.py
pixelpasta/lut_processor/cube_parser.py
pixelpasta/app.py
pixelpasta/lut_processor/color_analysis.py
pixelpasta/templates/upload.html
pixelpasta/tests/test_color_analysis.py

# Current Time
19/03/2025, 6:47:05 pm (Europe/Warsaw, UTC+1:00)

# Current Mode
ACT MODE
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file
import unittest
import numpy as np
import pandas as pd
from pixelpasta.lut_processor.color_analysis import slog3_curve, inverse_slog3_curve, rec709_oetf, interpolate_1d_lut, interpolate_3d_lut, srgb_to_rec709, generate_table, logc4_curve, inverse_logc4_curve
from pixelpasta.lut_processor.cube_parser import load_cube_file  # Importujemy, aby móc użyć w teście generate_table
import tempfile
import os

class TestColorAnalysis(unittest.TestCase):

    def test_slog3_curve(self):
        self.assertAlmostEqual(slog3_curve(0.0), 0.01)
        self.assertAlmostEqual(slog3_curve(0.1), 0.432699 * np.log10(0.1 + 0.009468) + 0.655)
        self.assertAlmostEqual(slog3_curve(1.0), 0.432699 * np.log10(1.0 + 0.009468) + 0.655)
        self.assertTrue(np.allclose(slog3_curve(np.array([0.0, 0.1, 1.0])), np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])))

    def test_inverse_slog3_curve(self):
        a = 0.432699
        b = 0.009468
        c = 0.655
        d = 0.037584
        e = 0.01
        V_threshold = slog3_curve(0.01125)
        self.assertTrue(np.allclose(inverse_slog3_curve(0.01), np.array([(0.01 - e) / d])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(0.1 + 0.009468) + 0.655), np.array([0.1])))
        self.assertTrue(np.allclose(inverse_slog3_curve(0.432699 * np.log10(1.0 + 0.009468) + 0.655), np.array([1.0])))
        self.assertTrue(np.allclose(inverse_slog3_curve(np.array([0.01, 0.432699 * np.log10(0.1 + 0.009468) + 0.655, 0.432699 * np.log10(1.0 + 0.009468) + 0.655])), np.array([ (0.01 - e) / d, 0.1, 1.0])))

    def test_rec709_oetf(self):
        self.assertAlmostEqual(rec709_oetf(0.0), 0.0)
        self.assertAlmostEqual(rec709_oetf(0.018), 0.08124794403514046)
        self.assertAlmostEqual(rec709_oetf(1.0), 1.0)
        self.assertTrue(np.allclose(rec709_oetf(np.array([0.0, 0.018, 1.0])), np.array([0.0, 0.08124794403514046, 1.0])))

    def test_interpolate_1d_lut(self):
        lut_1d = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([[0.0, 0.0, 0.0], [0.5, 0.5, 0.5], [1.0, 1.0, 1.0]])
        output = interpolate_1d_lut(lut_1d, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_interpolate_3d_lut(self):
        lut_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]
        ])
        lut_size = 2
        input_values = np.array([0.0, 0.5, 1.0])
        expected_output = np.array([
            [0.  , 0.  , 0.  ],
            [0.5 , 0.5 , 0.5 ],
            [1.  , 1.  , 1.  ]
        ])
        output = interpolate_3d_lut(lut_3d, lut_size, input_values, input_values, input_values)
        self.assertTrue(np.allclose(output, expected_output))

    def test_srgb_to_rec709(self):
        rgb_values = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        expected_output_sgamut3 = np.array([
            [ 1.641 , -0.6636,  0.0117],
            [-0.3245,  1.6157, -0.0085],
            [-0.3165,  0.0479,  0.9968]
        ])
        expected_output_sgamut3_cine = np.array([
            [ 1.5529, -0.5428, -0.0026],
            [-0.2555,  1.5027, -0.0186],
            [-0.2974,  0.0401,  1.0212]
        ])
        output_sgamut3 = srgb_to_rec709(rgb_values, 'S-Gamut3')
        output_sgamut3_cine = srgb_to_rec709(rgb_values, 'S-Gamut3.Cine')
        self.assertTrue(np.allclose(output_sgamut3, expected_output_sgamut3))
        self.assertTrue(np.allclose(output_sgamut3_cine, expected_output_sgamut3_cine))
        with self.assertRaises(ValueError):
            srgb_to_rec709(rgb_values, 'InvalidColorSpace')

    def test_generate_table(self):
        # Tworzymy tymczasowy plik .cube
        content = """
TITLE "Test LUT"
LUT_1D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".cube") as temp_file:
            temp_file.write(content.encode())
            filepath = temp_file.name

        # Testujemy dla S-Gamut3
        df_sgamut3 = generate_table(filepath, 'S-Gamut3')
        self.assertIsInstance(df_sgamut3, pd.DataFrame)
        self.assertEqual(len(df_sgamut3), 20)
        self.assertEqual(df_sgamut3['Color Space'][0], 'S-Gamut3')

        # Testujemy dla S-Gamut3.Cine
        df_sgamut3_cine = generate_table(filepath, 'S-Gamut3.Cine')
        self.assertIsInstance(df_sgamut3_cine, pd.DataFrame)
        self.assertEqual(len(df_sgamut3_cine), 20)
        self.assertEqual(df_sgamut3_cine['Color Space'][0], 'S-Gamut3.Cine')

        os.remove(filepath) # Usuwamy tymczasowy plik

    def test_logc4_curve(self):
      self.assertTrue(np.allclose(logc4_curve(0.0), np.array([-3852.359026659536])))
      self.assertAlmostEqual(logc4_curve(0.18), 0.4090068696819821)
      self.assertTrue(np.allclose(logc4_curve(np.array([0.0, 0.18, 1.0])), np.array([-3852.359026659536, 0.4090068696819821, 0.6577136499999999])))

    def test_inverse_logc4_curve(self):
      self.assertTrue(np.allclose(inverse_logc4_curve(0.09285527796717754), np.array([0.04345044])))
      self.assertTrue(np.allclose(inverse_logc4_curve(0.4090068696819821), np.array([0.18])))
      self.assertTrue(np.allclose(inverse_logc4_curve(np.array([0.09285527796717754, 0.4090068696819821, 0.6577136499999999])), np.array([0.04345044, 0.18, 1.0])))


if __name__ == '__main__':
    unittest.main()
