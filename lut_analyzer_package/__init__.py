"""
LUT Analyzer Package - Narzędzia do analizy i porównywania plików LUT (Look-Up Table).

Ten pakiet zawiera moduły do:
- Wczytywania i parsowania plików .cube
- Analizy LUT względem standardowych krzywych gamma i log
- Generowania raportów porównawczych w formacie PNG i PDF
- Obsługi różnych krzywych transferu (np. S-Log3, LogC, RED Log)
"""

# Importy z poszczególnych modułów dla ułatwienia dostępu
from lut_analyzer_package.lut_parsing import load_cube_file
from lut_analyzer_package.reporting import (
    compare_lut_to_curve,
    plot_lut_vs_curve,
    generate_pdf_report
)
from lut_analyzer_package.transfer_functions import *
from lut_analyzer_package.lut_interpolation import interpolate_1d_lut, interpolate_3d_lut
from lut_analyzer_package.color_space import s_gamut3_to_rec709, s_gamut3_cine_to_rec709

__version__ = "1.0.0"
