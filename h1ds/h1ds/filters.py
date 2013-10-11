"""Filters for h1ds data

TODO: Fefactor filters.

TODO: Need to test the following filters:
    - PulseWidth
    - MaxOf (scalar)

TODO:
    - 2D filters not working yet.

"""
from urlparse import urlparse, urlunparse
import urllib2
import json
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
    is_numpy_str = type(obj) in [np.string_, ]
    return all(hasattr(obj, attr) for attr in attrs) and not is_numpy_str


is_string = lambda cls, d: isinstance(d, basestring)


def http_arg(arg):
    if arg.startswith("http://"):
        # make sure we get the JSON  format, in case the user didn't add
        # format=json
        # Split URL into [scheme, netloc, path, params, query, fragments]
        parsed_url = urlparse(arg)

        # parsed_url is an immutable ParseResult  instance, copy it to a
        # (mutable) list
        parsed_url_list = [i for i in parsed_url]

        # Now we  can update the  URL query  string to enforce  the JSON
        # format.
        parsed_url_list[4] = '&'.join([parsed_url[4], 'format=json'])

        # And here is our original URL with format=json query added
        attr_url_json = urlunparse(parsed_url_list)
        request = urllib2.Request(attr_url_json)
        response = json.loads(urllib2.urlopen(request).read())

        return response['data']
    else:
        return arg


class BaseFilterMetaclass(type):
    def __new__(mcs, name, bases, dct):
        # assert  some classmethods  which  simplify the  API, so  users
        # don't  have  to  put  @classmethod in  front  of  each  filter
        # subclass
        classmethods = ["valid_dtype", ]
        for cm in classmethods:
            if dct.has_key(cm):
                dct[cm] = classmethod(dct[cm])
        return type.__new__(mcs, name, bases, dct)


@exclude_filter
class BaseFilter:
    __metaclass__ = BaseFilterMetaclass

    ndim = 0

    def __init__(self, **kwargs):
        self.kwargs = dict((k, http_arg(v)) for k, v in kwargs.iteritems())

    @classmethod
    def valid_ndim(cls, n_dim):
        return cls.ndim == "any" or n_dim == cls.ndim

    @classmethod
    def is_filterable(cls, data):
        return cls.valid_ndim(data.get_n_dimensions()) and cls.valid_dtype(data.value)

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
    """Cast data to float if string, or array if list."""
    if isinstance(data, list):
        return np.array(data)
    else:
        return float(data)


binary_powers = 2 ** np.arange(30)

########################################################################
## signal -> scalar                                                   ##
########################################################################


class FirstPulse(Array1DimNumericBaseFilter):
    """Return value of dim when the signal is greater than threshold.

    threshold can be a number or 'mid'.
    threshold = 'mid' will use (max(signal)+min(signal))/2
    """

    slug = "first_pulse"
    kwarg_names = ["threshold"]

    def apply(self, node):
        _threshold = self.kwargs["threshold"]
        if _threshold.lower() == 'mid':
            _threshold = (np.max(node.data.value) + np.min(node.data.value)) / 2
        else:
            _threshold = float(_threshold)

        first_element = np.where(node.data.value[0] > _threshold)[0][0]

        node.data.name = 'first_pulse(%s, %s)' % (node.data.name, self.kwargs["threshold"])
        node.data.value = node.data.dimension[0][first_element]
        node.data.dimension = []
        node.data.value_units = None
        node.data.dimension_units = None
        node.data.value_dtype = 'int'  # TODO: should we use dtypes rather than strings?
        node.data.dimension_dtype = None
        if len(node.data.value_labels) > 0:
            node.data.value_labels[0] = 'first_pulse(%s, %s)' % (node.data.value_labels[0], self.kwargs["threshold"])
        else:
            node.data.value_labels = [node.data.name]
        node.data.dimension_labels = []


class PulseWidth(Array1DimNumericBaseFilter):
    """
    pulse width...

    TODO: test this - it may be giving rubbish results...
    
    """
    slug = "pulse_width"
    kwarg_names = ["threshold"]

    def apply(self, node):
        _threshold = self.kwargs["threshold"]
        if _threshold.lower() == 'mid':
            _threshold = (np.max(node.data.value) + np.min(node.data.value)) / 2
        else:
            _threshold = float(_threshold)

        t = node.data.dimension[0][node.data.value[0] > _threshold]
        end1 = node.data.dimension[0][(node.data.value[0][:-1] - node.data.value[0][1:]) > _threshold]

        use_size = np.min([len(t), len(end1)])

        if use_size > 0:         # TODO: tell the user what's going on...
            node.data.name = "pulse_width(%s, %s)" % (node.data.name, self.kwargs["threshold"])
            node.data.value = np.min(end1[:use_size] - t[:use_size])
            node.data.dimension = []
            node.data.value_units = None
            node.data.dimension_units = None
            node.data.value_dtype = node.data.dimension_dtype
            node.data.dimension_dtype = None
            if len(node.data.value_labels) > 0:
                node.data.value_labels[0] = "pulse_width('%s', '%s')" % (
                    node.data.value_labels[0], self.kwargs["threshold"])
            else:
                node.data.value_labels = [node.data.name]
            node.data.dimension_labels = []


class PulseNumber(Array1DimNumericBaseFilter):
    slug = "pulse_number"
    kwarg_names = ["threshold"]

    def apply(self, node):
        """
        number of pulses...??

        """
        _threshold = self.kwargs["threshold"]
        if _threshold.lower() == 'mid':
            _threshold = (max(node.data.value) + min(node.data.value)) / 2
        else:
            _threshold = float(_threshold)

        t = node.data.dimension[0][node.data.value[0] > _threshold]
        end1 = node.data.dimension[0][(node.data.value[0][:-1] - node.data.value[0][1:]) > _threshold]

        # TODO: should no need to cast  this as int32, but there is some
        # bizarre problem with dtype_mapping  key... without casting the
        # result of np.min, type(node.data)  says it is numpy.int32, but
        # it   is  somehow   different   to  the   numpy.int32  in   the
        # dtype_mapping key.
        node.data.name = "pulse_number(%s, %s)" % (node.data.name, self.kwargs["threshold"])
        node.data.value = np.int32(np.min([t.shape[0], end1.shape[0]]))
        node.data.dimension = []
        node.data.value_units = None
        node.data.dimension_units = []
        node.data.value_dtype = "int"
        node.data.dimension_dtype = None
        if len(node.data.value_labels) > 0:
            node.data.value_labels[0] = "pulse_number(%s, %s)" % (node.data.value_labels[0], self.kwargs["threshold"])
        else:
            node.data.value_labels = [node.data.name]
        node.data.dimension_labels = []


class Max(Array1DimNumericBaseFilter):
    slug = "max"
    kwarg_names = []

    def apply(self, node):
        node.data.name = "max(%s)" % node.data.name
        node.data.value = np.max(node.data.value)
        # value_units, value_dtype unchanged
        node.data.dimension = []
        node.data.dimension_units = []
        node.data.dimension_dtype = None
        if len(node.data.value_labels) > 0:
            node.data.value_labels[0] = 'max(%s)' % (node.data.value_labels[0])
        else:
            node.data.value_labels = [node.data.name]
        node.data.dimension_labels = []


class MaxOf(Array1DimNumericBaseFilter):
    # TODO: this maps 1d to 1d, or scalar to scalar - not tested for scalar
    slug = "max_of"
    kwarg_names = ["value"]

    def apply(self, node):
        """Returns max(data, value).

        if the data is an array,  an array is returned with each element
        having max(data[element], value) value should be a float

        """
        _value = float(self.kwargs["value"])
        if isinstance(node.data.value[0], np.ndarray):
            node.data.value[0][node.data.value[0] < _value] = _value
        else:
            node.data.value = np.max([node.data.value[0], _value])

        node.data.name = "max_of(%s, %s)" % (node.data.name, self.kwargs["value"])
        if len(node.data.value_labels) > 0:
            node.data.value_labels[0] = "max_of(%s, %s)" % (node.data.value_labels[0], self.kwargs["value"])
        else:
            node.data.value_labels = [node.data.name]


class DimOfMaxVal(Array1DimNumericBaseFilter):
    """Returns dim at signal peak.

    """

    slug = "dim_of_max"
    kwarg_names = []

    def apply(self, node):
        node.data.name = "dim_of_max(%s)" % node.data.name
        node.data.value = node.data.dimension[0][np.argmax(node.data.value[0])]
        node.data.value_dtype = node.data.dimension_dtype
        node.data.value_units = node.data.dimension_units
        node.data.dimension = []
        node.data.dimension_dtype = None
        node.data.dimension_units = None
        if len(node.data.value_labels) > 0:
            node.data.value_labels[0] = "dim_of_max(%s)" % (node.data.value_labels[0])
        else:
            node.data.value_labels = [node.data.name]
        node.data.dimension_labels = []


class Mean(Array1DimNumericBaseFilter):
    slug = "mean"
    kwarg_names = []

    def apply(self, node):

        node.data.name = "mean(%s)" % node.data.name
        node.data.value = np.mean(node.data.value[0])
        node.data.dimension = []
        node.data.dimension_dtype = None
        node.data.dimension_units = None
        if len(node.data.value_labels) > 0:
            node.data.value_labels[0] = "mean(%s)" % (node.data.value_labels[0])
        else:
            node.data.value_labels = [node.data.name]
        node.data.dimension_labels = []


class Element(Array1DimNumericBaseFilter):
    """Get an element of an array.

    The first element has index 0.
    """

    slug = "element"
    kwarg_names = ["index"]

    def apply(self, node):
        _index = int(self.kwargs["index"])
        node.data.name = "index(%s, %s)" % (node.data.name, self.kwargs["index"])
        node.data.value = node.data.value[0][_index]
        node.data.dimension = []
        node.data.dimension_dtype = None
        node.data.dimension_units = None
        if len(node.data.value_labels) > 0:
            node.data.value_labels[0] = "index(%s, %s)" % (node.data.value_labels[0], self.kwargs["index"])
        else:
            node.data.value_labels = [node.data.name]
        node.data.dimension_labels = []


class PeakToPeak(Array1DimNumericBaseFilter):
    """Max(signal) - min(signal)."""

    slug = "peak_to_peak"
    kwarg_names = []

    def apply(self, node):
        node.data.name = "peak_to_peak(%s)" % node.data.name
        node.data.value = max(node.data.value[0]) - min(node.data.value[0])
        node.data.dimension = []
        node.data.dimension_dtype = None
        node.data.dimension_units = None
        if len(node.data.value_labels) > 0:
            node.data.value_labels[0] = "peak_to_peak(%s)" % (node.data.labels[0])
        else:
            node.data.value_labels = [node.data.name]
        node.data.dimension_labels = []

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
        start = np.mean(node.data.value[0][:_window])
        end = np.mean(node.data.value[0][-_window:])

        dim_len = node.data.value[0].shape[0]
        norm_dim = np.arange(dim_len, dtype=float) / (dim_len - 1)
        baseline = start + (end - start) * norm_dim

        node.data.name = "slanted_baseline(%s, %s)" % (node.data.name, self.kwargs["window"])
        node.data.value[0] -= baseline
        if len(node.data.value_labels) > 0:
            node.data.value_labels[0] = "slanted_baseline(%s, %s)" % (node.data.value_labels[0], self.kwargs["window"])
        else:
            node.data.value_labels = [node.data.name]


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
        n = int(0.5 + 0.5 / (dim[1] - dim[0]) / f0)
        a = np.cumsum(signal)
        if order > 1:
            return self._do_prl_lpn(
                self._do_prl_lpn(signal, dim, f0, order - 1), dim, f0, 1)
        else:
            return (a[n:] - a[:-n]) / float(n)

    def apply(self, node):
        _f0 = float(self.kwargs["f0"])
        _order = int(self.kwargs["order"])
        node.data.name = 'prl_lpn(%s, %s, %s)' % (node.data.name,
                                                  self.kwargs["f0"],
                                                  self.kwargs["order"])
        print len(node.data.value[0])
        print len(node.data.dimension[0])
        node.data.value = [self._do_prl_lpn(node.data.value[0], node.data.dimension[0], _f0, _order)]
        d_min = node.data.dimension[0][0]
        d_max = node.data.dimension[0][-1]
        len_signal = len(node.data.value[0])
        node.data.dimension = [d_min + (d_max - d_min) * np.arange(len_signal) / (len_signal - 1)]
        if len(node.data.value_labels) > 0:
            node.data.value_labels[0] = 'prl_lpn(%s, %s, %s)' % (node.data.value_labels[0],
                                                                 self.kwargs["f0"],
                                                                 self.kwargs["order"])
        else:
            node.data.value_labels = [node.data.name]


class Resample(Array1DimNumericBaseFilter):
    slug = "resample"
    kwarg_names = ["max_samples"]

    def apply(self, node):
        _max_samples = int(self.kwargs["max_samples"])
        signal_length = node.data.value[0].T.shape[0]
        delta_sample = signal_length / _max_samples

        node.data.name = "resample(%s, %s)" % (node.data.name, self.kwargs["max_samples"])
        # put trailing [:max_samples] in case we get an extra one at the end
        node.data.value = [node.data.value[0][::delta_sample][:_max_samples]]
        node.data.dimension = [node.data.dimension[0][::delta_sample][:_max_samples]]
        if len(node.data.value_labels) > 0:
            node.data.value_labels[0] = "resample(%s, %s)" % (node.data.value_label[0], self.kwargs["max_samples"])
        else:
            node.data.value_label = [node.data.name]


class ResampleMinMax(Array1DimNumericBaseFilter):
    """TODO: only works for 1D array..."""
    slug = "resample_minmax"
    kwarg_names = ["n_bins"]

    def apply(self, node):
        from h1ds.base import Data

        _n_bins = int(self.kwargs["n_bins"])
        signal_length = node.data.get_signal_length()
        if signal_length >= 2 * _n_bins:  # Only apply filter if length is more than 2*n_bins
            delta_sample = signal_length / _n_bins
            new_dimension = [node.data.dimension[0][::delta_sample][:_n_bins]]
            max_data = []
            min_data = []
            new_metadata = node.data.metadata

            for i in range(_n_bins):
                tmp = node.data.value[0][i * delta_sample:(i + 1) * delta_sample]
                max_data.append(max(tmp))
                min_data.append(min(tmp))

            new_metadata['minmax_pairs'] = [[0, 1]]
            new_metadata['original_name'] = node.data.name
            try:
                # TODO: should make sure labels are populated higher up the food chain...
                value_labels = ["min_rebinned(" + node.data.value_labels[0] + ")",
                                "max_rebinned(" + node.data.value_labels[0] + ")"]
            except:
                value_labels = ["min_rebinned", "max_rebinned"]
            new_data = Data(name="resampled_minmax(" + node.data.name + ")",
                            value=np.array([min_data, max_data]),
                            dimension=new_dimension,
                            value_units=node.data.value_units,
                            dimension_units=node.data.dimension_units,
                            value_dtype=node.data.value_dtype,
                            dimension_dtype=node.data.dimension_dtype,
                            value_labels=value_labels,
                            dimension_labels=node.data.dimension_labels,
                            metadata=new_metadata)
            node.data = new_data


class NormDimRange(Array1DimNumericBaseFilter):
    """Reduce range of signal."""

    slug = "norm_dim_range"
    kwarg_names = ["min", "max"]

    def apply(self, node):
        _min = float(self.kwargs["min"])
        _max = float(self.kwargs["max"])
        min_e, max_e = int(_min * len(node.data.dimension[0])), int(_max * len(node.data.dimension[0]))
        node.data.name = "normdim_range(%s, %s, %s)" % (node.data.name, self.kwargs["min"], self.kwargs["max"])
        node.data.value = [node.data.value[0][min_e:max_e]]
        node.data.dimension = [node.data.dimension[0][min_e:max_e]]
        if len(node.data.value_labels) > 0:
            node.data.value_labels[0] = "normdim_range(%s, %s, %s)" % (
                node.data.value_labels[0], self.kwargs["min"], self.kwargs["max"])
        else:
            node.data.value_labels = [node.data.name]


class DimRange(Array1DimNumericBaseFilter):
    """Reduce range of signal."""

    slug = "dim_range"
    kwarg_names = ["min", "max"]

    def apply(self, node):
        _min = float(self.kwargs["min"])
        _max = float(self.kwargs["max"])
        min_e, max_e = np.searchsorted(node.data.dimension[0], [_min, _max])
        node.data.name = "dim_range(%s, %s, %s)" % (node.data.name, self.kwargs["min"], self.kwargs["max"])
        node.data.value = [node.data.value[0][min_e:max_e]]
        node.data.dimension = [node.data.dimension[0][min_e:max_e]]

        if len(node.data.value_labels) > 0:
            node.data.value_labels[0] = "dim_range(%s, %s, %s)" % (
                node.data.value_labels[0], self.kwargs["min"], self.kwargs["max"])
        else:
            node.data.value_labels = [node.data.name]


class PowerSpectrum(Array1DimNumericBaseFilter):
    """power spectrum of signal."""

    slug = "power_spectrum"
    kwarg_names = []

    def apply(self, node):
        output_size = 2 ** np.searchsorted(binary_powers, node.data.value[0].shape[0])

        node.data.name = "power_spectrum(%s)" % node.data.name
        node.data.value = [np.abs(np.fft.fft(node.data.value[0], n=output_size))]
        length = len(node.data.value[0])
        sample_rate = np.mean(node.data.dimension[0][1:] - node.data.dimension[0][:-1])
        node.data.dimension = [(1. / sample_rate) * np.arange(length) / (length - 1)]
        node.data.dimension_units = "1/%s" % node.data.dimension_units

        if len(node.data.value_labels) > 0:
            node.data.value_labels[0] = "power_spectrum(%s)" % (node.data.value_labels[0])
        else:
            node.data.value_labels = [node.data.name]


# TODO: generalise energy limits between 1d and 2d signals.
# TODO: this is really dumb, inefficient algorithm, can do much better.
class XAxisEnergyLimit(Array1DimNumericBaseFilter):
    """for 1d signal, limit range to include fraction of total energy"""

    slug = "x_axis_energy_limit"
    kwarg_names = ["threshold"]

    def x_axis_energy_limit(self, node):
        _threshold = float(self.kwargs["threshold"])

        ## TODO: need to get x,y dimensions standardised for matrix
        ## which dimension should be which??

        total_power = np.sum(node.data.value[0].ravel() ** 2)

        removed_power = 0
        while removed_power < (1 - _threshold) * total_power:
            lower = node.data.value[0][0] ** 2
            upper = node.data.value[0][-1] ** 2
            if (min(lower, upper) + removed_power) > _threshold * total_power:
                break
            if lower < upper:
                node.data.value = [node.data.value[0][1:]]
                node.data.dimension = [node.data.dimension[0][1:]]
                removed_power += lower
            else:
                node.data.value = [node.data.value[0][:-1]]
                node.data.dimension = [node.data.dimension[0][:-1]]
                removed_power += upper
        node.data.name = "x_axis_energy_limit(%s, %s)" % (node.data.name, self.kwargs["threshold"])
        if len(node.data.value_labels) > 0:
            node.data.labels[0] = "x_axis_energy_limit(%s, %s)" % (node.data.value_labels[0], self.kwargs["threshold"])
        else:
            node.data.labels = [node.data.name]

    def apply(self, node):
        self.x_axis_energy_limit(node)


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

        node.data.name = "(%s)*%s" % (self.kwargs["factor"], node.data.name)
        node.data.value = _factor * node.data.value
        if len(node.data.value_labels) > 0:
            node.data.value_labels[0] = "(%s)*%s" % (self.kwargs["factor"], node.data.value_labels[0])
        else:
            node.data.value_labels = [node.data.name]


class Divide(BaseFilter):
    """Divide data by scale factor"""

    slug = "divide"
    ndim = "any"
    valid_dtype = is_numeric
    kwarg_names = ["factor"]

    def apply(self, node):
        _factor = float(self.kwargs["factor"])

        node.data.name = "(%s)/%s" % (node.data.name, self.kwargs["factor"])
        node.data.value /= _factor
        if len(node.data.value_labels) > 0:
            node.data.value_labels[0] = "(%s)/%s" % (node.data.value_labels[0], self.kwargs["factor"])
        else:
            node.data.value_labels = [node.data.name]


class Subtract(BaseFilter):
    """Subtract the value.

    """
    slug = "subtract"
    ndim = "any"
    valid_dtype = is_numeric
    kwarg_names = ["value"]

    def apply(self, node):
        _value = float(self.kwargs["value"])

        node.data.name = "%s - %s" % (node.data.name, self.kwargs["value"])
        node.data.value -= _value
        if len(node.data.value_labels) > 0:
            node.data.value_labels[0] = "%s - %s" % (node.data.value_labels[0], self.kwargs["value"])
        else:
            node.data.value_labels = [node.data.name]


class Add(BaseFilter):
    """Add the value.

    """
    slug = "add"
    ndim = "any"
    valid_dtype = is_numeric
    kwarg_names = ["value"]

    def apply(self, node):
        _value = float(self.kwargs["value"])

        node.data.name = "%s + %s" % (node.data.name, self.kwargs["value"])
        node.data.value += _value
        if len(node.data.value_labels) > 0:
            node.data.value_labels[0] = "%s + %s" % (node.data.value_labels[0], self.kwargs["value"])
        else:
            node.data.value_labels = [node.data.name]


class Exponent(BaseFilter):
    """Raise data to the (value)th power."""

    slug = "exponent"
    ndim = "any"
    valid_dtype = is_numeric
    kwarg_names = ["value"]

    def apply(self, node):
        _value = float(self.kwargs["value"])

        node.data.name = "(%s)^%s" % (node.data.name, self.kwargs["value"])
        node.data.value **= _value
        if len(node.data.value_labels) > 0:
            node.data.value_labels[0] = "(%s)^%s" % (node.data.value_labels[0], self.kwargs["value"])
        else:
            node.data.value_labels = [node.data.name]


## ########################################################################
## ## 1d signals -> 2d                                                   ##
## ########################################################################
## class Spectrogram(Array1DimNumericBaseFilter):
##     """spectrogram of signal. use bin_size=-1 for auto"""

##     slug = "spectrogram"
##     kwarg_names = ["bin_size"]

##     def apply(self, node):
##         _bin_size = int(self.kwargs["bin_size"])
##         if _bin_size < 0:
##             # have a guess...
##             approx_bin_size = np.sqrt(len(node.dim))
##             _bin_size = 2**np.searchsorted(binary_powers, approx_bin_size)
##         sample_rate = np.mean(node.dim[1:] - node.dim[:-1])

##         new_x_dim = node.dim[::_bin_size]
##         norm_dim = np.arange(_bin_size, dtype=float)/(_bin_size-1)
##         new_y_dim = (1./sample_rate)*norm_dim

##         #new_y_dim = new_y_dim[:_bin_size/2]

##         new_data = []
##         for t_el in np.arange(len(node.data))[::_bin_size]:
##             fft_ = np.fft.fft(node.data[t_el:t_el+_bin_size], n=_bin_size)
##             new_data.append(np.abs(fft_[:_bin_size]).tolist())

##         node.data = np.array(new_data)

##         # TODO: this is  a hack because I don't  properly understand how
##         # numpy determines  dtypes - if  new x and  y dims are  the same
##         # then it will have dtype of  float, etc. if different length it
##         # will be object dtype object dtype  is what we are using, as we
##         # can get different lengths for different dimensions. (Should we
##         # even use a  numpy array? How does MDSplus perfer  to deal with
##         # higher  dim  signals? -  we  should  use  the same  format  as
##         # MDSplus). Anyway - it seems that even if we assert dtype to be
##         # object
##         # >>> q=np.array([[1,2,3],[2,3,4]], dtype=np.object)
##         # >>> q[1] = q[1][:2] ** fails
##         # it fails when we later try and have different shaped elements.
##         # So, let's create node.dim as something we know we can resizt
##         node.dim = np.array([[None], [None, None]])
##         node.dim[0] = new_x_dim.tolist()
##         node.dim[1] = new_y_dim.tolist()

##         node.labels = ('spectrogram(%s,%d)' %(node.labels[0], _bin_size), )



## ########################################################################
## ## 2d signals                                                         ##
## ########################################################################

## class Shape(Array2DimNumericBaseFilter):
##     """Shape of image"""

##     slug = "shape"
##     kwarg_names = []

##     def apply(self, node):
##         node.data = {"rows":node.data.shape[0],
##                         "columns":node.data.shape[1]}
##         node.dim = None
##         node.labels = ('shape(%s)' %(node.labels[0]),)

## class Transpose(Array2DimNumericBaseFilter):
##     """Transpose a 2d array"""

##     slug = "transpose"
##     kwarg_names = []

##     def apply(self, node):
##         node.data = np.transpose(node.data)
##         #TODO: how to treat dim?
##         node.labels = ('transpose(%s)' %(node.labels[0]),)

## class FlipVertical(Array2DimNumericBaseFilter):
##     """Flip array vertically"""

##     slug = "flip_vertical"
##     kwarg_names = []

##     def apply(self, node):
##         tmp_data = node.data.copy()
##         for r in xrange(tmp_data.shape[0]/2):
##             node.data[r, :] = tmp_data[-(r+1), :]
##             node.data[-(r+1), :] = tmp_data[r, :]
##         #TODO: how to treat dim?
##         node.labels = ('vertical_flip(%s)' %(node.labels[0]),)

## class FlipHorizontal(Array2DimNumericBaseFilter):
##     """Flip array horizontally"""

##     slug = "flip_horizontal"
##     kwarg_names = []

##     def apply(self, node):
##         tmp_data = node.data.copy()
##         for c in xrange(tmp_data.shape[1]/2):
##             node.data[:, c] = tmp_data[:, -(c+1)]
##             node.data[:, -(c+1)] = tmp_data[:, c]
##         #TODO: how to treat dim?
##         node.labels = ('horizontal_flip(%s)' %(node.labels[0]),)

## class NormDimRange2D(Array2DimNumericBaseFilter):
##     """Reduce range of signal."""

##     slug = "norm_dim_range_2d"
##     kwarg_names = ["x_min", "x_max", "y_min", "y_max"]
##     def apply(self, node):
##         _min_x_val = float(self.kwargs["x_min"])
##         _max_x_val = float(self.kwargs["x_max"])
##         _min_y_val = float(self.kwargs["y_min"])
##         _max_y_val = float(self.kwargs["y_max"])

##         min_xe = int(_min_x_val*len(node.dim[0]))
##         max_xe = int(_max_x_val*len(node.dim[0]))
##         min_ye = int(_min_y_val*len(node.dim[1]))
##         max_ye = int(_max_y_val*len(node.dim[1]))

##         node.data = node.data[min_xe:max_xe, min_ye:max_ye]
##         node.dim[0] = node.dim[0][min_xe:max_xe]
##         node.dim[1] = node.dim[1][min_ye:max_ye]
##         node.labels = ('2d_normdim_range(%s, %s, %s, %s, %s)' %(
##             node.labels[0], self.kwargs["x_min"],
##             self.kwargs["x_max"], self.kwargs["y_min"],
##             self.kwargs["y_max"]),)

## class YAxisEnergyLimit(Array2DimNumericBaseFilter):
##     "2D reduce y-axis range to threshold*100% of total signal energy"

##     slug = "y_axis_energy_limit"
##     kwarg_names = ["threshold"]

##     def apply(self, node):
##         _threshold = float(self.kwargs["threshold"])

##         ## TODO: need to get x,y dimensions standardised for matrix
##         ## which dimension should be which??

##         total_power = np.sum(node.data.ravel()**2)

##         # if the result  is going to be less  than min_y_resolution then
##         # don't do it.
##         min_y_resolution = 10

##         low_counter = 0
##         high_counter = -1
##         removed_power = 0
##         while removed_power < (1-_threshold)*total_power:
##             lower = np.sum(node.data[:, low_counter]**2)
##             upper = np.sum(node.data[:, high_counter]**2)
##             if (min(lower, upper) + removed_power) > _threshold*total_power:
##                 break
##             if lower < upper:
##                 removed_power += lower
##                 low_counter += 1
##             else:
##                 removed_power += upper
##                 high_counter -= 1
##         if len(node.dim[1][low_counter:high_counter]) > min_y_resolution:
##             node.data = node.data[:, low_counter:high_counter]
##             node.dim[1] = node.dim[1][low_counter:high_counter]

## ########################################################################
## ## Other                                                              ##
## ########################################################################

## class DimOf(BaseFilter):
##     """Return the dim of the data as the data."""
##     slug = "dim_of"
##     ndim = "any"
##     valid_dtype = is_numeric
##     kwarg_names = []

##     def apply(self, node):
##         node.data = node.dim
##         node.dim = np.arange(len(node.data))
##         node.labels = ('dim_of(%s)' %(node.labels[0]),)

## class Cast(BaseFilter):
##     """Recast dtype"""
##     slug = "cast"
##     ndim = "any"
##     valid_dtype = is_numeric
##     kwarg_names = ["dtype"]

##     def apply(self, node):
##         cast_dtype = getattr(np, self.kwargs["dtype"])
##         node.data = cast_dtype(node.data)
##         node.dim = cast_dtype(node.dim)
