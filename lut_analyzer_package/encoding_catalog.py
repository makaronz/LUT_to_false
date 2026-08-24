"""Shared LUT input encoding catalog (valid transfer + gamut pairs only)."""

from lut_analyzer_package.color_space import (
    aces_ap1_to_rec709,
    arri_wide_gamut3_to_rec709,
    arri_wide_gamut4_to_rec709,
    canon_cinema_gamut_to_rec709,
    red_wide_gamut_rgb_to_rec709,
    s_gamut3_cine_to_rec709,
    s_gamut3_to_rec709,
    v_gamut_to_rec709,
)
from lut_analyzer_package.transfer_functions import (
    acescct_to_linear,
    canonlog2_to_linear,
    linear_to_acescct,
    linear_to_canonlog2,
    linear_to_log3g10,
    linear_to_logc3,
    linear_to_logc4,
    linear_to_rec709,
    linear_to_red_ipp2_odt_approx,
    linear_to_redgamma3,
    linear_to_redgamma4,
    linear_to_redlogfilm,
    linear_to_slog2,
    linear_to_slog3,
    linear_to_slog3_cine,
    linear_to_vlog,
    log3g10_to_linear,
    logc3_to_linear,
    logc4_to_linear,
    rec709_to_linear,
    red_ipp2_odt_approx_to_linear,
    redgamma3_to_linear,
    redgamma4_to_linear,
    redlogfilm_to_linear,
    slog2_to_linear,
    slog3_cine_to_linear,
    slog3_to_linear,
    vlog_to_linear,
)

DEFAULT_ENCODING = "slog3_cine"

ENCODING_INFO = {
    "slog3": {
        "curve_func": linear_to_slog3,
        "inverse_func": slog3_to_linear,
        "color_space": "sgamut3",
        "color_transform": s_gamut3_to_rec709,
        "transfer": "S-Log3",
        "gamut": "S-Gamut3",
        "description": "Sony S-Log3 (S-Gamut3)",
        "group": "Sony",
        "gamut_transform_available": True,
    },
    "slog3_cine": {
        "curve_func": linear_to_slog3_cine,
        "inverse_func": slog3_cine_to_linear,
        "color_space": "sgamut3_cine",
        "color_transform": s_gamut3_cine_to_rec709,
        "transfer": "S-Log3",
        "gamut": "S-Gamut3.Cine",
        "description": "Sony S-Log3 (S-Gamut3.Cine)",
        "group": "Sony",
        "gamut_transform_available": True,
    },
    "slog2": {
        "curve_func": linear_to_slog2,
        "inverse_func": slog2_to_linear,
        "color_space": "sgamut3",
        "color_transform": s_gamut3_to_rec709,
        "transfer": "S-Log2",
        "gamut": "S-Gamut3",
        "description": "Sony S-Log2 (S-Gamut3)",
        "group": "Sony",
        "gamut_transform_available": True,
    },
    "logc4": {
        "curve_func": linear_to_logc4,
        "inverse_func": logc4_to_linear,
        "color_space": "arri_wide_gamut4",
        "color_transform": arri_wide_gamut4_to_rec709,
        "transfer": "LogC4",
        "gamut": "ARRI Wide Gamut 4",
        "description": "ARRI LogC4 (Wide Gamut 4)",
        "group": "ARRI",
        "gamut_transform_available": True,
    },
    "logc3": {
        "curve_func": linear_to_logc3,
        "inverse_func": logc3_to_linear,
        "color_space": "arri_wide_gamut3",
        "color_transform": arri_wide_gamut3_to_rec709,
        "transfer": "LogC3",
        "gamut": "ARRI Wide Gamut 3",
        "description": "ARRI LogC3 (Wide Gamut 3)",
        "group": "ARRI",
        "gamut_transform_available": True,
    },
    "log3g10": {
        "curve_func": linear_to_log3g10,
        "inverse_func": log3g10_to_linear,
        "color_space": "red_wide_gamut_rgb",
        "color_transform": red_wide_gamut_rgb_to_rec709,
        "transfer": "Log3G10",
        "gamut": "RED Wide Gamut RGB",
        "description": "RED Log3G10 (REDWideGamutRGB)",
        "group": "RED",
        "gamut_transform_available": True,
    },
    "redgamma3": {
        "curve_func": linear_to_redgamma3,
        "inverse_func": redgamma3_to_linear,
        "color_space": "red_wide_gamut_rgb",
        "color_transform": red_wide_gamut_rgb_to_rec709,
        "transfer": "REDgamma3",
        "gamut": "RED Wide Gamut RGB",
        "description": "RED Gamma 3",
        "group": "RED",
        "gamut_transform_available": True,
    },
    "redgamma4": {
        "curve_func": linear_to_redgamma4,
        "inverse_func": redgamma4_to_linear,
        "color_space": "red_wide_gamut_rgb",
        "color_transform": red_wide_gamut_rgb_to_rec709,
        "transfer": "REDgamma4",
        "gamut": "RED Wide Gamut RGB",
        "description": "RED Gamma 4",
        "group": "RED",
        "gamut_transform_available": True,
    },
    "redlogfilm": {
        "curve_func": linear_to_redlogfilm,
        "inverse_func": redlogfilm_to_linear,
        "color_space": "red_wide_gamut_rgb",
        "color_transform": red_wide_gamut_rgb_to_rec709,
        "transfer": "REDlogFilm",
        "gamut": "RED Wide Gamut RGB",
        "description": "RED Log Film",
        "group": "RED",
        "gamut_transform_available": True,
    },
    "red_ipp2_odt_approx": {
        "curve_func": linear_to_red_ipp2_odt_approx,
        "inverse_func": red_ipp2_odt_approx_to_linear,
        "color_space": "red_wide_gamut_rgb",
        "color_transform": red_wide_gamut_rgb_to_rec709,
        "transfer": "RED IPP2 ODT approx",
        "gamut": "RED Wide Gamut RGB",
        "description": "RED IPP2 ODT Approximation",
        "group": "RED",
        "gamut_transform_available": True,
    },
    "vlog": {
        "curve_func": linear_to_vlog,
        "inverse_func": vlog_to_linear,
        "color_space": "v_gamut",
        "color_transform": v_gamut_to_rec709,
        "transfer": "V-Log",
        "gamut": "V-Gamut",
        "description": "Panasonic V-Log (V-Gamut)",
        "group": "Panasonic",
        "gamut_transform_available": True,
    },
    "canonlog2": {
        "curve_func": linear_to_canonlog2,
        "inverse_func": canonlog2_to_linear,
        "color_space": "canon_cinema_gamut",
        "color_transform": canon_cinema_gamut_to_rec709,
        "transfer": "Canon Log 2",
        "gamut": "Canon Cinema Gamut",
        "description": "Canon Log 2 (Cinema Gamut)",
        "group": "Canon",
        "gamut_transform_available": True,
    },
    "rec709": {
        "curve_func": linear_to_rec709,
        "inverse_func": rec709_to_linear,
        "color_space": "rec709",
        "color_transform": None,
        "transfer": "Rec.709",
        "gamut": "Rec.709",
        "description": "Rec.709",
        "group": "Display",
        "gamut_transform_available": True,
    },
    "acescct": {
        "curve_func": linear_to_acescct,
        "inverse_func": acescct_to_linear,
        "color_space": "aces_ap1",
        "color_transform": aces_ap1_to_rec709,
        "transfer": "ACEScct",
        "gamut": "ACES AP1",
        "description": "ACEScct (AP1)",
        "group": "ACES",
        "gamut_transform_available": True,
    },
}

ENCODING_ALIASES = {
    "gamma22": "redgamma4",
    "gamma24": "redgamma3",
    "clog2": "canonlog2",
    "redipp2odt": "red_ipp2_odt_approx",
}

ENCODING_GROUPS = (
    "Sony",
    "ARRI",
    "RED",
    "Panasonic",
    "Canon",
    "Display",
    "ACES",
)


def resolve_encoding(encoding_key):
    """Resolve an encoding key or alias to a catalog entry."""
    if not isinstance(encoding_key, str) or not encoding_key.strip():
        raise ValueError("encoding must be a non-empty string")

    key = encoding_key.strip()
    if key in ENCODING_ALIASES:
        key = ENCODING_ALIASES[key]
    if key not in ENCODING_INFO:
        raise ValueError(f"Unknown encoding: {encoding_key}")
    return key, ENCODING_INFO[key]


def encoding_options_for_ui():
    """Return grouped options for HTML selects."""
    groups = []
    for group_name in ENCODING_GROUPS:
        options = [
            {"value": key, "label": info["description"]}
            for key, info in ENCODING_INFO.items()
            if info["group"] == group_name
        ]
        if options:
            groups.append({"name": group_name, "options": options})
    return groups


def encoding_contract(encoding_key):
    """Serializable encoding metadata for analysis contracts."""
    key, info = resolve_encoding(encoding_key)
    return {
        "key": key,
        "description": info["description"],
        "transfer": info["transfer"],
        "gamut": info["gamut"],
        "gamut_transform": (
            "available" if info.get("gamut_transform_available") else "unavailable"
        ),
    }
