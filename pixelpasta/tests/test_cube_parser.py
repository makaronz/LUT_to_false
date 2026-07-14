import unittest
import numpy as np
from pixelpasta.lut_processor.cube_parser import load_cube_file
import tempfile
import os

class TestCubeParser(unittest.TestCase):

    def create_temp_cube_file(self, content):
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".cube")
        with open(temp_file.name, 'w') as f:
            f.write(content)
        return temp_file.name

    def test_valid_1d_lut(self):
        content = """
TITLE "Test 1D LUT"
LUT_1D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
"""
        filepath = self.create_temp_cube_file(content)
        lut_data = load_cube_file(filepath)
        self.assertEqual(lut_data['title'], '"Test 1D LUT"')
        self.assertEqual(lut_data['lut_type'], '1D')
        self.assertEqual(lut_data['lut_1d_size'], 2)
        self.assertTrue(np.array_equal(lut_data['lut_1d'], np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])))
        os.remove(filepath)

    def test_valid_3d_lut(self):
        content = """
TITLE "Test 3D LUT"
LUT_3D_SIZE 2
0.0 0.0 0.0
0.0 0.0 1.0
0.0 1.0 0.0
0.0 1.0 1.0
1.0 0.0 0.0
1.0 0.0 1.0
1.0 1.0 0.0
1.0 1.0 1.0
"""
        filepath = self.create_temp_cube_file(content)
        lut_data = load_cube_file(filepath)
        self.assertEqual(lut_data['title'], '"Test 3D LUT"')
        self.assertEqual(lut_data['lut_type'], '3D')
        self.assertEqual(lut_data['lut_3d_size'], 2)
        expected_lut_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]
        ])
        self.assertTrue(np.array_equal(lut_data['lut_3d'], expected_lut_3d))
        os.remove(filepath)

    def test_valid_both_luts(self):
        content = """
TITLE "Test Both LUTs"
LUT_1D_SIZE 2
LUT_3D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
0.0 0.0 0.0
0.0 0.0 1.0
0.0 1.0 0.0
0.0 1.0 1.0
1.0 0.0 0.0
1.0 0.0 1.0
1.0 1.0 0.0
1.0 1.0 1.0
"""
        filepath = self.create_temp_cube_file(content)
        lut_data = load_cube_file(filepath)
        self.assertEqual(lut_data['title'], '"Test Both LUTs"')
        self.assertEqual(lut_data['lut_type'], 'both')
        self.assertEqual(lut_data['lut_1d_size'], 2)
        self.assertEqual(lut_data['lut_3d_size'], 2)
        self.assertTrue(np.array_equal(lut_data['lut_1d'], np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])))
        expected_lut_3d = np.array([
            [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0], [0.0, 1.0, 1.0],
            [1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]
        ])
        self.assertTrue(np.array_equal(lut_data['lut_3d'], expected_lut_3d))
        os.remove(filepath)

    def test_invalid_lut_size(self):
        content = """
LUT_1D_SIZE 0
0.0 0.0 0.0
1.0 1.0 1.0
"""
        filepath = self.create_temp_cube_file(content)
        with self.assertRaisesRegex(ValueError, "Błąd w linii 2: Nieprawidłowa wartość LUT_1D_SIZE"):
            load_cube_file(filepath)
        os.remove(filepath)

    def test_invalid_lut3d_size(self):
        content = """
LUT_3D_SIZE 1
0.0 0.0 0.0
0.0 0.0 1.0
"""
        filepath = self.create_temp_cube_file(content)
        # Rozmiar 3D LUT < 2 jest nieprawidłowy.
        with self.assertRaisesRegex(ValueError, "Nieprawidłowa wartość LUT_3D_SIZE"):
            load_cube_file(filepath)
        os.remove(filepath)

    def test_invalid_domain_min(self):
        content = """
DOMAIN_MIN a b c
LUT_1D_SIZE 2
0.0 0.0 0.0
1.0 1.0 1.0
"""
        filepath = self.create_temp_cube_file(content)
        with self.assertRaisesRegex(ValueError, "Błąd w linii 2: Nieprawidłowe wartości DOMAIN_MIN"):
            load_cube_file(filepath)
        os.remove(filepath)

    def test_invalid_data(self):
        content = """
LUT_1D_SIZE 2
0.0 0.0 a
1.0 1.0 1.0
"""
        filepath = self.create_temp_cube_file(content)
        with self.assertRaisesRegex(ValueError, "Błąd w linii 3: could not convert string to float: 'a'"):
            load_cube_file(filepath)
        os.remove(filepath)

    def test_empty_file(self):
        content = ""
        filepath = self.create_temp_cube_file(content)
        with self.assertRaisesRegex(ValueError, "Plik jest pusty"):
            load_cube_file(filepath)
        os.remove(filepath)

    def test_comments(self):
        content = """
# Komentarz
TITLE "Test LUT"
# Komentarz
LUT_1D_SIZE 2
0.0 0.0 0.0
# Komentarz
1.0 1.0 1.0
"""
        filepath = self.create_temp_cube_file(content)
        lut_data = load_cube_file(filepath)
        self.assertEqual(lut_data['title'], '"Test LUT"')
        self.assertEqual(lut_data['lut_1d_size'], 2)
        os.remove(filepath)

    def test_lut_1d_size_after_data(self):
        content = """
TITLE "Test LUT"
0.0 0.0 0.0
1.0 1.0 1.0
LUT_1D_SIZE 2
"""
        filepath = self.create_temp_cube_file(content)
        with self.assertRaisesRegex(ValueError, "LUT_1D_SIZE zadeklarowane po danych LUT"):
            load_cube_file(filepath)
        os.remove(filepath)

    def test_lut_3d_size_after_data(self):
        content = """
TITLE "Test LUT"
0.0 0.0 0.0
0.0 0.0 1.0
0.0 1.0 0.0
0.0 1.0 1.0
1.0 0.0 0.0
1.0 0.0 1.0
1.0 1.0 0.0
1.0 1.0 1.0
LUT_3D_SIZE 2
"""
        filepath = self.create_temp_cube_file(content)
        with self.assertRaisesRegex(ValueError, "LUT_3D_SIZE zadeklarowane po danych LUT"):
            load_cube_file(filepath)
        os.remove(filepath)

if __name__ == '__main__':
    unittest.main()
