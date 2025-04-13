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
        if isinstance(slog3, np.ndarray):
            result = np.zeros_like(slog3)
            low_range = slog3 < 171.2102946929 / 1023.0
            high_range = ~low_range
            
            result[low_range] = (slog3[low_range] * 1023.0 / 95.0) - (171.2102946929 / 95.0)
            result[high_range] = np.power(10.0, ((slog3[high_range] * 1023.0 - 420.0) / 261.5)) * (0.18 + 0.01) - 0.01
            return result
        else:
            if slog3 < 171.2102946929 / 1023.0:
                return (slog3 * 1023.0 / 95.0) - (171.2102946929 / 95.0)
            else:
                return np.power(10.0, ((slog3 * 1023.0 - 420.0) / 261.5)) * (0.18 + 0.01) - 0.01
    
    @staticmethod
    def linear_to_slog3(linear):
        """
        Linear to S-Log3 conversion
        Based on Sony's S-Log3 specification
        """
        if isinstance(linear, np.ndarray):
            result = np.zeros_like(linear)
            low_range = linear < 0.01125000
            high_range = ~low_range
            
            result[low_range] = (95.0 * linear[low_range] + 171.2102946929) / 1023.0
            result[high_range] = (420.0 + 261.5 * np.log10((linear[high_range] + 0.01) / (0.18 + 0.01))) / 1023.0
            return result
        else:
            if linear < 0.01125000:
                return (95.0 * linear + 171.2102946929) / 1023.0
            else:
                return (420.0 + 261.5 * np.log10((linear + 0.01) / (0.18 + 0.01))) / 1023.0
    
    @staticmethod
    def logc_to_linear(logc):
        """
        ARRI LogC to linear conversion (EI 800, SUP 3.x)
        """
        if isinstance(logc, np.ndarray):
            result = np.zeros_like(logc)
            low_range = logc < 0.1496582
            high_range = ~low_range
            
            # LogC parameters for EI 800
            cut = 0.010591
            a = 5.555556
            b = 0.052272
            c = 0.247190
            d = 0.385537
            e = 5.367655
            f = 0.092809
            
            result[low_range] = (logc[low_range] - c) / a
            result[high_range] = (np.power(10.0, (logc[high_range] - d) / e) - f) / b
            return result
        else:
            # LogC parameters for EI 800
            cut = 0.010591
            a = 5.555556
            b = 0.052272
            c = 0.247190
            d = 0.385537
            e = 5.367655
            f = 0.092809
            
            if logc < 0.1496582:
                return (logc - c) / a
            else:
                return (np.power(10.0, (logc - d) / e) - f) / b
    
    @staticmethod
    def linear_to_logc(linear):
        """
        Linear to ARRI LogC conversion (EI 800, SUP 3.x)
        """
        if isinstance(linear, np.ndarray):
            result = np.zeros_like(linear)
            low_range = linear < 0.010591
            high_range = ~low_range
            
            # LogC parameters for EI 800
            cut = 0.010591
            a = 5.555556
            b = 0.052272
            c = 0.247190
            d = 0.385537
            e = 5.367655
            f = 0.092809
            
            result[low_range] = c + a * linear[low_range]
            result[high_range] = d + e * np.log10(b * linear[high_range] + f)
            return result
        else:
            # LogC parameters for EI 800
            cut = 0.010591
            a = 5.555556
            b = 0.052272
            c = 0.247190
            d = 0.385537
            e = 5.367655
            f = 0.092809
            
            if linear < cut:
                return c + a * linear
            else:
                return d + e * np.log10(b * linear + f)
    
    @staticmethod
    def redlog3g10_to_linear(redlog):
        """
        RED Log3G10 to linear conversion
        """
        if isinstance(redlog, np.ndarray):
            return (np.power(10.0, (redlog - 0.616596 - 0.03) / 0.224282) - 1) / 155.975327
        else:
            return (np.power(10.0, (redlog - 0.616596 - 0.03) / 0.224282) - 1) / 155.975327
    
    @staticmethod
    def linear_to_redlog3g10(linear):
        """
        Linear to RED Log3G10 conversion
        """
        if isinstance(linear, np.ndarray):
            return 0.224282 * np.log10(155.975327 * linear + 1.0) + 0.616596 + 0.03
        else:
            return 0.224282 * np.log10(155.975327 * linear + 1.0) + 0.616596 + 0.03
    
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