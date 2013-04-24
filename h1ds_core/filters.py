"""Filters for h1ds data
"""
from urlparse import urlparse, urlunparse
import urllib2, json
from django.core.urlresolvers import reverse
import numpy as np

excluded_filters = set()

def exclude_filter(original_class):
    """Decorator to mark subclasses of BaseFilter which aren't useable filters.

    Use, for example, with  ScalarNumericBaseFilter which is designed to
    be subclassed to form usable filters.
    
    """
    #original_class.__exclude_filter = True
    global excluded_filters
    excluded_filters.add(original_class)
    return original_class

def is_numeric(cls, obj):
    attrs = ['__add__', '__sub__', '__mul__', '__div__', '__pow__']
    # numpy string_ have these attrs, do any others?
    is_numpy_str = type(obj) in [np.string_,]
    return all(hasattr(obj, attr) for attr in attrs) and not is_numpy_str

is_string = lambda cls, d: isinstance(d, basestring)
    
def http_arg(arg):
    if arg.startswith("http://"):
        # make sure we get the JSON format, in case the user didn't add format=json
        # Split URL into [scheme, netloc, path, params, query, fragments]
        parsed_url = urlparse(arg)

        # parsed_url is an immutable ParseResult instance, copy it to a (mutable) list
        parsed_url_list = [i for i in parsed_url]

        # Now we can update the URL query string to enforce the JSON format.
        parsed_url_list[4] = '&'.join([parsed_url[4], 'format=json'])

        # And here is our original URL with format=json query added
        attr_url_json = urlunparse(parsed_url_list)
        request = urllib2.Request(attr_url_json)
        response = json.loads(urllib2.urlopen(request).read())

        return response['data']
    else:
        return arg

class BaseFilterMetaclass(type):
    def __new__(cls, name, bases, dct):
        # assert  some classmethods  which  simplify the  API, so  users
        # don't  have  to  put  @classmethod in  front  of  each  filter
        # subclass
        classmethods = ["valid_dtype", ]
        for cm in classmethods:
            if dct.has_key(cm):
                dct[cm] = classmethod(dct[cm])
        return type.__new__(cls, name, bases, dct)

@exclude_filter
class BaseFilter:

    __metaclass__ = BaseFilterMetaclass

    def __init__(self, **kwargs):
        self.kwargs = dict((k, http_arg(v)) for k,v in kwargs.iteritems())
    
    @classmethod
    def is_filterable(cls, data):
        ndim = data.ndim if hasattr(data, 'ndim') else 0
        return (ndim == cls.ndim or cls.ndim == "any") and cls.valid_dtype(data)

    @classmethod
    def get_slug(cls):
        return cls.slug

@exclude_filter
class ScalarNumericBaseFilter(BaseFilter):

    ndim = 0
    valid_dtype = is_numeric

@exclude_filter
class ScalarStringBaseFilter(BaseFilter):

    ndim = 0
    valid_dtype = is_string

@exclude_filter
class Array1DimNumericBaseFilter(BaseFilter):
    
    ndim = 1
    valid_dtype = is_numeric

@exclude_filter
class Array2DimNumericBaseFilter(BaseFilter):
    
    ndim = 2
    valid_dtype = is_numeric
    

def float_or_array(data):
    """Data will probably be a string or a list, convert it to a float or np array."""
    if isinstance(data, list):
        return np.array(data)
    else:
        return float(data)


binary_powers = 2**np.arange(30)

########################################################################
## signal -> scalar                                                   ##
########################################################################

class FirstPulse(Array1DimNumericBaseFilter):
    """Return first dimension (i.e. time) when the signal is greater than threshold.

    threshold can be a number or 'mid'.
    threshold = 'mid' will use (max(signal)+min(signal))/2
    """

    
    slug = "first_pulse"
    kwarg_names = ["threshold"]
    
    def apply(self, node):
        _threshold = self.kwargs["threshold"]
        if _threshold.lower() == 'mid':
            _threshold = (max(node.data)+min(node.data))/2
        else:
            _threshold = float(_threshold)

        first_element = np.where(node.data>_threshold)[0][0]
        node.data = node.dim[first_element]
        node.dim = None
        node.label = ('first_pulse(%s, %s)' %(node.label[0], self.kwargs["threshold"]), )
        

class PulseWidth(Array1DimNumericBaseFilter):
    """
    pulse width...

    """
    slug = "pulse_width"
    kwarg_names = ["threshold"]

    def apply(self, node):
        _threshold = self.kwargs["threshold"]
        if _threshold.lower() == 'mid':
            _threshold = (max(node.data)+min(node.data))/2
        else:
            _threshold = float(_threshold)

        t = node.dim[node.data>_threshold]
        end1 = node.dim[(node.data[:-1]-node.data[1:])>_threshold]

        use_size = min([len(t), len(end1)])

        node.data = np.min(end1[:use_size]-t[:use_size])
        node.dim = None
        node.label = ('pulse_width(%s, %s)' %(node.label[0], self.kwargs["threshold"]), )
    

class PulseNumber(Array1DimNumericBaseFilter):

    slug = "pulse_number"
    kwarg_names = ["threshold"]
            
    def apply(self, node):
        """
        number of pulses...??

        """
        _threshold = self.kwargs["threshold"]
        if _threshold.lower() == 'mid':
            _threshold = (max(node.data)+min(node.data))/2
        else:
            _threshold = float(_threshold)

        t = node.dim[node.data>_threshold]
        end1 = node.dim[(node.data[:-1]-node.data[1:])>_threshold]

        # TODO: should no need to cast this as int32, but there is some bizarre problem
        # with dtype_mapping key... without casting the result of np.min, type(node.data)
        # says it is numpy.int32, but it is somehow different to the numpy.int32 in the dtype_mapping key.
        node.data = np.int32(np.min([t.shape[0], end1.shape[0]]))
        node.dim = None
        node.label = ('pulse_number(%s, %s)' %(node.label[0], self.kwargs["threshold"]), )


class Max(Array1DimNumericBaseFilter):
    
    slug = "max"
    kwarg_names = []
    
    def apply(self, node):
        node.data = np.max(node.data)
        node.dim = None
        node.label = ('max(%s)' %node.label[0],)

class MaxOf(Array1DimNumericBaseFilter):

    slug = "max_of"
    kwarg_names = ["value"]

        
    def apply(self, node):
        """Returns max(data, value).

        if the data is an array, an array is returned with each element having max(data[element], value)
        value should be a float

        """
        _value = float(self.kwargs["value"])
        if isinstance(node.data, np.ndarray):
            node.data[node.data<_value] = _value
        else:
            node.data =  np.max([node.data, _value])
        node.label = ('max_of(%s, %s)' %(node.label[0], self.kwargs["values"]),)

class DimOfMaxVal(Array1DimNumericBaseFilter):
    """Returns dim at signal peak.

    """

    slug = "dim_of_max"
    kwarg_names = []
    
    def apply(self, node):
        node.data = node.dim[np.argmax(node.data)]
        node.dim = None
        node.label = ('dim_of_max(%s)' %node.label[0],)

class Mean(Array1DimNumericBaseFilter):

    slug = "mean"
    kwarg_names = []
    
    def apply(self, node):
        if len(node.data) > 0:
            node.data = np.mean(node.data)
        else:
            node.data = None
        node.dim = None
        node.label = ('mean(%s)' %node.label[0],)

class Element(Array1DimNumericBaseFilter):
    """Get an element of an array.

    The first element has index 0.
    """

    slug = "element"
    kwarg_names = ["index"]

    def apply(self, node):
        _index = int(self.kwargs["index"])
        node.data = node.data[_index]
        node.dim = None
        node.label = ('%s[%s]' %(node.label[0], self.kwargs["index"]),)

class PeakToPeak(Array1DimNumericBaseFilter):
    """Max(signal) - min(signal)."""

    slug = "peak_to_peak"
    kwarg_names = []

    def apply(self, node):
        node.data = max(node.data) - min(node.data)
        node.dim = None
        node.label = ('max(%(lab)s)-min(%(lab)s)' %{'lab':node.label[0]},)

class NSignals(Array1DimNumericBaseFilter):
    """Single trace returns 1, images return > 1

    Deprecated...
    """

    slug = "n_signals"
    kwarg_names = []
    
    def apply(self, node):
        """Single trace returns 1, images return > 1"""
        node.data = np.int16(node.data.ndim)
        node.dim = None
        node.label = ('n_signals(%(lab)s)' %{'lab':node.label[0]},)

########################################################################
## signal -> signal                                                   ##
########################################################################

class SlantedBaseline(Array1DimNumericBaseFilter):
    """Remove linear baseline.

    window must be an integer.

    endpoints are computed at the first (window) and last (window) samples.

    """

    slug = "slanted_baseline"
    kwarg_names = ["window"]

    
    def apply(self, node):
        _window = int(self.kwargs["window"])
        start = np.mean(node.data[:_window])
        end = np.mean(node.data[-_window:])

        baseline = start + (end-start)*np.arange(node.data.shape[0], dtype=float)/(node.data.shape[0]-1)
        node.data -= baseline
        node.label = ('slanted_baseline(%(lab)s, %(win)s)' %{'lab':node.label[0], 'win':self.kwargs["window"]},)

class PrlLpn(Array1DimNumericBaseFilter):
    """prl_lpn

    TODO: only working for order = 1
    """
    slug = "prl_lpn"
    kwarg_names = ["f0", "order"]
    
    def _do_prl_lpn(self, signal, dim, f0, order):
        """This  function is required  to handle  the recursion  in prl_lpn.

        Handle  only the  signal,  not  the data  wrapper.  Also, we  assume
        arguments have already been cast to numeric types.
        """
        N = int(0.5 + 0.5/(dim[1]-dim[0])/f0)
        a = np.cumsum(signal)
        if order > 1:
            return self._do_prl_lpn(self._do_prl_lpn(signal, dim, f0, order-1), dim, f0, 1)
        else:
            return (a[N:]-a[:-N])/float(N)
    
    def apply(self, node):
        _f0 = float(self.kwargs["f0"])
        _order = int(self.kwargs["order"])
        node.data = self._do_prl_lpn(node.data, node.dim, _f0, _order)
        node.label = ('prl_lpn(%s, %s, %s)' %(node.label[0], self.kwargs["f0"], self.kwargs["order"]),)

class Resample(Array1DimNumericBaseFilter):
    slug = "resample"
    kwarg_names = ["max_samples"]
   
    def apply(self, node):
        _max_samples = int(self.kwargs["max_samples"])
        signal_length = node.data.T.shape[0]
        delta_sample = signal_length/_max_samples

        # put trailing [:max_samples] in case we get an extra one at the end
        node.data = node.data[::delta_sample][:_max_samples]
        node.dim = node.dim[::delta_sample][:_max_samples]
        node.label = ('resample(%s, %s)' %(node.label[0], self.kwargs["max_samples"]),)

class ResampleMinMax(Array1DimNumericBaseFilter):
    """TODO: only works for 1D array..."""
    slug = "resample_minmax"
    kwarg_names = ["n_bins"]
    
    def apply(self, node):

        _n_bins = int(self.kwargs["n_bins"])

        signal_length = node.data.T.shape[0]
        if signal_length >= 2*_n_bins:
            delta_sample = signal_length/_n_bins
            node.dim = node.dim[::delta_sample][:_n_bins]
            max_data = []
            min_data = []

            for i in range(_n_bins):
                tmp = node.data[i*delta_sample:(i+1)*delta_sample]
                max_data.append(max(tmp))
                min_data.append(min(tmp))

            node.label = ('min', 'max',)
            node.data = np.array([min_data, max_data])

class NormDimRange(Array1DimNumericBaseFilter):
    """Reduce range of signal."""

    slug = "norm_dim_range"
    kwarg_names = ["min", "max"]
    
    def apply(self, node):
        _min = float(self.kwargs["min"])
        _max = float(self.kwargs["max"])
        min_e, max_e = int(_min*len(node.dim)), int(_max*len(node.dim))
        node.data = node.data[min_e:max_e]
        node.dim = node.dim[min_e:max_e]
        node.label = ('normdim_range(%s, %s, %s)' %(node.label[0], self.kwargs["min"], self.kwargs["max"]),)

class DimRange(Array1DimNumericBaseFilter):
    """Reduce range of signal."""

    slug = "dim_range"
    kwarg_names = ["min", "max"]
    
    def apply(self, node):
        _min = float(self.kwargs["min"])
        _max = float(self.kwargs["max"])
        min_e, max_e = np.searchsorted(node.dim, [_min, _max])
        node.data = node.data[min_e:max_e]
        node.dim = node.dim[min_e:max_e]
        node.label = ('dim_range(%s, %s, %s)' %(node.label[0], self.kwargs["min"], self.kwargs["max"]),)

class PowerSpectrum(Array1DimNumericBaseFilter):
    """power spectrum of signal."""

    slug = "power_spectrum"
    kwarg_names = []
    
    def apply(self, node):
        output_size = 2**np.searchsorted(binary_powers, node.data.shape[0])
        node.data = np.abs(np.fft.fft(node.data, n=output_size))
        length = len(node.data)
        sample_rate = np.mean(node.dim[1:] - node.dim[:-1])
        node.dim = (1./sample_rate)*np.arange(length)/(length-1)
        node.label = ('power_spectrum(%s)' %(node.label[0]),)

# TODO: generalise energy limits between 1d and 2d signals.
class XAxisEnergyLimit(Array1DimNumericBaseFilter):
    """for 1d signal, limit range to include fraction of total energy"""

    slug = "x_axis_energy_limit"
    kwarg_names = ["threshold"]

    def x_axis_energy_limit(self, node):
        _threshold = float(self.kwargs["threshold"])

        ## TODO: need to get x,y dimensions standardised for matrix
        ## which dimension should be which??

        total_power = np.sum(node.data.ravel()**2)

        removed_power = 0
        while removed_power < (1-_threshold)*total_power:
            lower = node.data[0]**2
            upper = node.data[-1]**2
            if (min(lower, upper) + removed_power) > _threshold*total_power:
                break
            if lower < upper:
                node.data = node.data[1:]
                node.dim = node.dim[1:]
                removed_power += lower
            else:
                node.data = node.data[:-1]
                node.dim = node.dim[:-1]
                removed_power += upper


########################################################################
## scalar or vector -> same                                           ##
########################################################################

class Multiply(BaseFilter):
    """Multiply data by scale factor"""

    slug = "multiply"
    ndim = "any"
    valid_dtype = is_numeric
    kwarg_names = ["factor"]

    def apply(self, node):

        _factor = float_or_array(self.kwargs["factor"])

        node.data = _factor*node.data
        node.label = ('%s*(%s)' %(self.kwargs["factor"], node.label[0]),)


class Divide(BaseFilter):
    """Divide data by scale factor"""

    slug = "divide"
    ndim = "any"
    valid_dtype = is_numeric
    kwarg_names = ["factor"]

    def apply(self, node):
        _factor = float(self.kwargs["factor"])
        node.data = node.data/_factor
        node.label = ('(%s)/%s' %(node.label[0], self.kwargs["factor"]),)

class Subtract(BaseFilter):
    """Subtract the value.

    """
    slug = "subtract"
    ndim = "any"
    valid_dtype = is_numeric
    kwarg_names = ["value"]
            
    def apply(self, node):
        _value = float(self.kwargs["value"])

        node.data = node.data - _value
        node.label = ('%s - %s' %(node.label[0], self.kwargs["value"]),)

class Add(BaseFilter):        
    """Add the value.

    """
    slug = "subtract"
    ndim = "any"
    valid_dtype = is_numeric
    kwarg_names = ["value"]
    def apply(self, node):
        _value = float(self.kwargs["value"])

        node.data = node.data + _value
        node.label = ('%s + %s' %(node.label[0], self.kwargs["value"]),)

class Exponent(BaseFilter):        
    """Raise data to the (value)th power."""

    slug = "exponent"
    ndim = "any"
    valid_dtype = is_numeric
    kwarg_names = ["value"]

    def apply(self, node):
        _value =float(self.kwargs["value"])
        node.data = node.data**_value
        node.label = ('%s^%s' %(node.label[0], self.kwargs["value"]),)


########################################################################
## 1d signals -> 2d                                                   ##
########################################################################
class Spectrogram(Array1DimNumericBaseFilter):
    """spectrogram of signal. use bin_size=-1 for auto"""

    slug = "spectrogram"
    kwarg_names = ["bin_size"]
    
    def apply(self, node):
        _bin_size =int(self.kwargs["bin_size"])
        if _bin_size < 0:
            # have a guess...
            approx_bin_size = np.sqrt(len(node.dim))
            _bin_size=2**np.searchsorted(binary_powers, approx_bin_size)
        sample_rate = np.mean(node.dim[1:] - node.dim[:-1])

        new_x_dim = node.dim[::_bin_size]
        new_y_dim = (1./sample_rate)*np.arange(_bin_size,dtype=float)/(_bin_size-1)

        #new_y_dim = new_y_dim[:_bin_size/2]

        new_data = []
        for t_el in np.arange(len(node.data))[::_bin_size]:
            #new_data.append(np.abs(np.fft.fft(node.data[t_el:t_el+_bin_size],n=_bin_size)[:_bin_size/2]).tolist())
            new_data.append(np.abs(np.fft.fft(node.data[t_el:t_el+_bin_size],n=_bin_size)[:_bin_size]).tolist())

        node.data = np.array(new_data)

        # TODO: this is a hack because I don't properly understand how numpy
        # determines dtypes - if new x and y dims are the same then it will have
        # dtype of float, etc. if different length it will be object dtype
        # object dtype is what we are using, as we can get different lengths for
        # different dimensions. (Should we even use a numpy array? How does MDSplus
        # perfer to deal with higher dim signals? - we should use the same format as
        # MDSplus). Anyway - it seems that even if we assert dtype to be object
        # >>> q=np.array([[1,2,3],[2,3,4]], dtype=np.object)
        # >>> q[1] = q[1][:2] ** fails
        # it fails when we later try and have different shaped elements.
        # So, let's create node.dim as something we know we can resizt
        node.dim = np.array([[None],[None, None]])
        node.dim[0] = new_x_dim.tolist()
        node.dim[1] = new_y_dim.tolist()

        node.label = ('spectrogram(%s,%d)' %(node.label[0],_bin_size),)



########################################################################
## 2d signals                                                         ##
########################################################################

class Shape(Array2DimNumericBaseFilter):
    """Shape of image"""

    slug = "shape"
    kwarg_names = []
    
    def apply(self, node):
        node.data = {"rows":node.data.shape[0],
                        "columns":node.data.shape[1]}
        node.dim = None
        node.label = ('shape(%s)' %(node.label[0]),)

class Transpose(Array2DimNumericBaseFilter):
    """Transpose a 2d array"""

    slug = "transpose"
    kwarg_names = []
    
    def apply(self, node):
        node.data = np.transpose(node.data)
        #TODO: how to treat dim?
        node.label = ('transpose(%s)' %(node.label[0]),)

class FlipVertical(Array2DimNumericBaseFilter):
    """Flip array vertically"""

    slug = "flip_vertical"
    kwarg_names = []
    
    def apply(self, node):
        tmp_data = node.data.copy()
        for r in xrange(tmp_data.shape[0]/2):
            node.data[r,:] = tmp_data[-(r+1),:]
            node.data[-(r+1),:] = tmp_data[r,:]
        #TODO: how to treat dim?
        node.label = ('vertical_flip(%s)' %(node.label[0]),)

class FlipHorizontal(Array2DimNumericBaseFilter):
    """Flip array horizontally"""

    slug = "flip_horizontal"
    kwarg_names = []
    
    def apply(self, node):
        tmp_data = node.data.copy()
        for c in xrange(tmp_data.shape[1]/2):
            node.data[:,c] = tmp_data[:,-(c+1)]
            node.data[:,-(c+1)] = tmp_data[:,c]
        #TODO: how to treat dim?
        node.label = ('horizontal_flip(%s)' %(node.label[0]),)

class NormDimRange2D(Array2DimNumericBaseFilter):
    """Reduce range of signal."""

    slug = "norm_dim_range_2d"
    kwarg_names = ["x_min", "x_max", "y_min", "y_max"]
    def apply(self, node):
        _min_x_val = float(self.kwargs["x_min"])
        _max_x_val = float(self.kwargs["x_max"])
        _min_y_val = float(self.kwargs["y_min"])
        _max_y_val = float(self.kwargs["y_max"])

        min_xe, max_xe = int(_min_x_val*len(node.dim[0])), int(_max_x_val*len(node.dim[0]))
        min_ye, max_ye = int(_min_y_val*len(node.dim[1])), int(_max_y_val*len(node.dim[1]))

        node.data = node.data[min_xe:max_xe,min_ye:max_ye]
        node.dim[0] = node.dim[0][min_xe:max_xe]
        node.dim[1] = node.dim[1][min_ye:max_ye]
        node.label = ('2d_normdim_range(%s, %s, %s, %s, %s)' %(node.label[0], self.kwargs["x_min"], self.kwargs["x_max"], self.kwargs["y_min"], self.kwargs["y_max"]),)

class YAxisEnergyLimit(Array2DimNumericBaseFilter):
    "2D reduce y-axis range to threshold*100% of total signal energy"
    
    slug = "y_axis_energy_limit"
    kwarg_names = ["threshold"]
    
    def apply(self, node):
        _threshold = float(self.kwargs["threshold"])

        ## TODO: need to get x,y dimensions standardised for matrix
        ## which dimension should be which??

        total_power = np.sum(node.data.ravel()**2)

        # if the result is going to be less than min_y_resolution then don't do it.
        min_y_resolution = 10

        low_counter = 0
        high_counter = -1
        removed_power = 0
        while removed_power < (1-_threshold)*total_power:
            lower = np.sum(node.data[:,low_counter]**2)
            upper = np.sum(node.data[:,high_counter]**2)
            if (min(lower, upper) + removed_power) > _threshold*total_power:
                break
            if lower < upper:
                removed_power += lower
                low_counter += 1
            else:
                removed_power += upper
                high_counter -= 1
        if len(node.dim[1][low_counter:high_counter]) > min_y_resolution:
            node.data = node.data[:,low_counter:high_counter]
            node.dim[1] = node.dim[1][low_counter:high_counter]

########################################################################
## Other                                                              ##
########################################################################

class DimOf(BaseFilter):
    """Return the dim of the data as the data."""
    slug = "dim_of"
    ndim = "any"
    valid_dtype = is_numeric
    kwarg_names = []

    def apply(self, node):
        node.data = node.dim
        node.dim = np.arange(len(node.data))
        node.label = ('dim_of(%s)' %(node.label[0]),)
