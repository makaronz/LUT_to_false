import numpy as np

class TransferFunctions:
    """
    Standard camera and display transfer functions
    Includes both gamma and log transformations used in professional
    video and cinema production
    """
    
    @staticmethod
    def linear_to_rec709(linear):
        """
        Convert from linear to Rec.709 gamma curve
        """
        if isinstance(linear, np.ndarray):
            result = np.zeros_like(linear)
            low_range = linear <= 0.018
            high_range = ~low_range
            
            # Rec.709 piecewise function
            result[low_range] = 4.5 * linear[low_range]
            result[high_range] = 1.099 * np.power(linear[high_range], 0.45) - 0.099
            return result
        else:
            if linear <= 0.018:
                return 4.5 * linear
            else:
                return 1.099 * np.power(linear, 0.45) - 0.099
    
    @staticmethod
    def rec709_to_linear(gamma):
        """
        Convert from Rec.709 gamma curve to linear
        """
        if isinstance(gamma, np.ndarray):
            result = np.zeros_like(gamma)
            low_range = gamma <= 0.081
            high_range = ~low_range
            
            # Rec.709 inverse piecewise function
            result[low_range] = gamma[low_range] / 4.5
            result[high_range] = np.power((gamma[high_range] + 0.099) / 1.099, 1/0.45)
            return result
        else:
            if gamma <= 0.081:
                return gamma / 4.5
            else:
                return np.power((gamma + 0.099) / 1.099, 1/0.45)
    
    @staticmethod
    def srgb_to_linear(srgb):
        """
        Convert from sRGB to linear
        """
        if isinstance(srgb, np.ndarray):
            result = np.zeros_like(srgb)
            low_range = srgb <= 0.04045
            high_range = ~low_range
            
            result[low_range] = srgb[low_range] / 12.92
            result[high_range] = np.power((srgb[high_range] + 0.055) / 1.055, 2.4)
            return result
        else:
            if srgb <= 0.04045:
                return srgb / 12.92
            else:
                return np.power((srgb + 0.055) / 1.055, 2.4)
    
    @staticmethod
    def linear_to_srgb(linear):
        """
        Convert from linear to sRGB
        """
        if isinstance(linear, np.ndarray):
            result = np.zeros_like(linear)
            low_range = linear <= 0.0031308
            high_range = ~low_range
            
            result[low_range] = 12.92 * linear[low_range]
            result[high_range] = 1.055 * np.power(linear[high_range], 1/2.4) - 0.055
            return result
        else:
            if linear <= 0.0031308:
                return 12.92 * linear
            else:
                return 1.055 * np.power(linear, 1/2.4) - 0.055
    
    @staticmethod
    def linear_to_gamma(linear, gamma=2.4):
        """
        Apply standard gamma curve (used for pure power functions)
        """
        return np.power(linear, 1/gamma)
    
    @staticmethod
    def gamma_to_linear(gamma_val, gamma=2.4):
        """
        Inverse standard gamma curve (used for pure power functions)
        """
        return np.power(gamma_val, gamma)
    
    @staticmethod
    def slog3_to_linear(slog3):
        """
        S-Log3 to linear conversion
        Based on Sony's S-Log3 specification
        """
        scalar = not isinstance(slog3, np.ndarray)
        s = np.asarray(slog3, dtype=np.float64)
        cv = s * 1023.0
        result = np.where(
            cv >= 171.2102946929,
            np.power(10.0, (cv - 420.0) / 261.5) * (0.18 + 0.01) - 0.01,
            (cv - 95.0) * 0.01125 / (171.2102946929 - 95.0),
        )
        return float(result) if scalar else result

    @staticmethod
    def linear_to_slog3(linear):
        """
        Linear to S-Log3 conversion
        Based on Sony's S-Log3 specification
        """
        scalar = not isinstance(linear, np.ndarray)
        lin = np.asarray(linear, dtype=np.float64)
        result = np.where(
            lin >= 0.01125,
            (420.0 + 261.5 * np.log10((lin + 0.01) / (0.18 + 0.01))) / 1023.0,
            (lin * (171.2102946929 - 95.0) / 0.01125 + 95.0) / 1023.0,
        )
        return float(result) if scalar else result
    
    # ARRI LogC3 EI800 parameters (encode: t = c*log10(a*x+b)+d for x>cut,
    # else e*x+f; decode is the exact inverse). The previous implementation
    # scrambled these roles and produced values like -4.93 for 18% grey.
    _LOGC = dict(cut=0.010591, a=5.555556, b=0.052272,
                 c=0.247190, d=0.385537, e=5.367655, f=0.092809)

    @staticmethod
    def logc_to_linear(logc):
        """
        ARRI LogC3 to linear conversion (EI 800)
        """
        p = TransferFunctions._LOGC
        scalar = not isinstance(logc, np.ndarray)
        t = np.asarray(logc, dtype=np.float64)
        log_cut = p['e'] * p['cut'] + p['f']  # 0.149658
        result = np.where(
            t > log_cut,
            (np.power(10.0, (t - p['d']) / p['c']) - p['b']) / p['a'],
            (t - p['f']) / p['e'],
        )
        return float(result) if scalar else result

    @staticmethod
    def linear_to_logc(linear):
        """
        Linear to ARRI LogC3 conversion (EI 800)
        """
        p = TransferFunctions._LOGC
        scalar = not isinstance(linear, np.ndarray)
        x = np.asarray(linear, dtype=np.float64)
        result = np.where(
            x > p['cut'],
            p['c'] * np.log10(p['a'] * x + p['b']) + p['d'],
            p['e'] * x + p['f'],
        )
        return float(result) if scalar else result
    
    @staticmethod
    def redlog3g10_to_linear(redlog):
        """
        RED Log3G10 (v2) to linear conversion
        """
        scalar = not isinstance(redlog, np.ndarray)
        y = np.asarray(redlog, dtype=np.float64)
        x = np.where(y >= 0.0,
                     (np.power(10.0, y / 0.224282) - 1.0) / 155.975327,
                     y / 15.1927)
        result = x - 0.01
        return float(result) if scalar else result

    @staticmethod
    def linear_to_redlog3g10(linear):
        """
        Linear to RED Log3G10 (v2) conversion.
        y = 0.224282*log10(x'*155.975327+1) for x' >= 0 (x' = linear+0.01),
        else y = x'*15.1927. The previous +0.616596 offset was spurious.
        """
        scalar = not isinstance(linear, np.ndarray)
        x = np.asarray(linear, dtype=np.float64) + 0.01
        result = np.where(x >= 0.0,
                          0.224282 * np.log10(x * 155.975327 + 1.0),
                          x * 15.1927)
        return float(result) if scalar else result
    
    @staticmethod
    def vlog_to_linear(vlog):
        """
        Panasonic V-Log to linear conversion
        """
        if isinstance(vlog, np.ndarray):
            cut1 = 0.01
            b = 0.00873
            c = 0.241514
            d = 0.598206
            
            result = np.zeros_like(vlog)
            low_range = vlog < 0.181
            high_range = ~low_range
            
            result[low_range] = (vlog[low_range] - 0.125) / 5.6
            result[high_range] = np.power(10.0, (vlog[high_range] - d) / c) - b
            return result
        else:
            cut1 = 0.01
            b = 0.00873
            c = 0.241514
            d = 0.598206
            
            if vlog < 0.181:
                return (vlog - 0.125) / 5.6
            else:
                return np.power(10.0, (vlog - d) / c) - b
    
    @staticmethod
    def linear_to_vlog(linear):
        """
        Linear to Panasonic V-Log conversion
        """
        if isinstance(linear, np.ndarray):
            cut1 = 0.01
            b = 0.00873
            c = 0.241514
            d = 0.598206
            
            result = np.zeros_like(linear)
            low_range = linear < 0.01
            high_range = ~low_range
            
            result[low_range] = 5.6 * linear[low_range] + 0.125
            result[high_range] = c * np.log10(linear[high_range] + b) + d
            return result
        else:
            cut1 = 0.01
            b = 0.00873
            c = 0.241514
            d = 0.598206
            
            if linear < cut1:
                return 5.6 * linear + 0.125
            else:
                return c * np.log10(linear + b) + d 