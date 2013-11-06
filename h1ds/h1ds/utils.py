"""
A "smart compression" replacement for savez, assuming data is quantised.

The quantum is found, and the data  replaced by a product of and integer
sequence and quantum with offset.   delta encoding is optional and often
saves  space.  The  efficiency  is better  than bz2  of  ascii data  for
individual  channels, and  a little  worse if  many channels  are lumped
together  with  a common  timebase  in  the  bz2 ascii  format,  because
save_compress stores individual timebases.

$ wc -c /f/python/local_data/027/27999_P*  2300176 total

At the moment  (2010), save_compress is not explicitly  implemented - it
is effected by calling discretise_signal() with a filename argument.

July 2009  - long-standing error  in delta_encode_signal fixed  (had not
been usable before)

Original Author: Boyd Blackwell.

"""
import inspect
import numpy as np
from django.utils.importlib import import_module
from django.conf import settings
from h1ds.base import BaseBackendShotManager


def discretise_array(arr, eps=0, bits=0, maxcount=0, delta_encode=False):
    """
    Return  an integer  array  and  scales etc  in  a  dictionary -  the
    dictionary form  allows for  added functionaility.  If  bits=0, find
    the  natural accuracy.   eps  defaults  to 3e-6,  and  is the  error
    relative to the larest element, as is maxerror.
    """
    if eps == 0:
        eps = 3e-6
    if maxcount == 0:
        maxcount = 10
    count = 1
    ans = try_discretise_array(arr, eps=eps, bits=bits,
                               delta_encode=delta_encode)
    initial_deltar = ans['deltar']
    # look for timebase, because they have the largest ratio of value to
    # step size, and  are the hardest to discretise in  presence of repn
    # err.  better  check positive!  Could  add code to  handle negative
    # later.
    if initial_deltar > 0:
        # find the largest power of 10 smaller than initial_deltar
        p10r = np.log10(initial_deltar)
        p10int = int(100 + p10r) - 100   # always round down
        ratiop10 = initial_deltar / 10 ** p10int
        eps10 = abs(round(ratiop10) - ratiop10)
        if eps10 < 3e-3 * ratiop10:
            initial_deltar = round(ratiop10) * 10 ** p10int
            ans = try_discretise_array(arr, eps=eps, bits=bits,
                                       deltar=initial_deltar,
                                       delta_encode=delta_encode)
            initial_deltar = ans['deltar']

    while (ans['maxerror'] > eps) and (count < maxcount):
        count += 1
        # have faith in our guess, assume problem is that step is
        # not the minimum.  e.g. arr=[1,3,5,8] 
        #          - min step is 2, natural step is 1
        ans = try_discretise_array(arr, eps=eps, bits=bits,
                                   deltar=initial_deltar / count,
                                   delta_encode=delta_encode)

    return ans

#    return(ans.update({'count':count})) # need to add in count


def try_discretise_array(arr, eps=0, bits=0, deltar=None, delta_encode=False):
    """
    Return an integer array and scales etc in a dictionary 
    - the dictionary form allows for added functionaility.
    If bits=0, find the natural accuracy.  eps defaults to 1e-6
    """
    if eps == 0:
        eps = 1e-6
    if deltar is not None:
        data_sort = np.unique(arr)
        # don't want uniques because of noise
        diff_sort = np.sort(np.diff(data_sort))
        if np.size(diff_sort) == 0:
            diff_sort = [0]  # in case all the same

        # with real  representation, there  will be many  diffs ~  eps -
        # 1e-8 or 1e-15*max - try to skip over these
        #  will have at least three cases 
        #    - timebase with basically one diff and all diffdiffs in the
        #    noise
        #    - data with lots  of diffs and lots of diffdiffs  at a much
        #    lower level

        min_real_diff_ind = (diff_sort > np.max(diff_sort) / 1e4).nonzero()
        if np.size(min_real_diff_ind) == 0:
            min_real_diff_ind = [[0]]
            # min_real_diff_ind[0] is the array  of inidices satisfying that
        # condition
        # discard all preceding this
        diff_sort = diff_sort[min_real_diff_ind[0][0]:]
        deltar = diff_sort[0]
        diff_diff_sort = np.diff(diff_sort)
        # now look  for the  point where the  diff of  differences first
        # exceeds half the current estimate of difference

        # the  diff of  differences  should just  be the  discretization
        # noise  by  looking further  down  the  sorted diff  array  and
        # averaging over  elements which are  close in value to  the min
        # real difference,  we can  reduce the effect  of discretization
        # error.
        large_diff_diffs_ind = (abs(diff_diff_sort) > deltar / 2).nonzero()
        if np.size(large_diff_diffs_ind) == 0:
            last_small_diff_diffs_ind = len(diff_sort) - 1
        else:
            first_large_diff_diffs_ind = large_diff_diffs_ind[0][0]
            last_small_diff_diffs_ind = first_large_diff_diffs_ind - 1

        # When the  step size is  within a few orders  of represeantaion
        # accuracy, problems  appear if there a  systematic component in
        # the representational noise.

        # Could try to limit the  number of samples averaged over, which
        # would be  very effective when  the timebase starts  from zero.
        # MUST NOT sort the difference first in this case!  Better IF we
        # can   reliably  detect   single  rate   timebase,  then   take
        # (end-start)/(N-1)       if       last_small_diff_diffs_ind>10:
        # last_small_diff_diffs_ind=2 This limit would only work if time
        # started at  zero.  A smarter way  would be to find  times near
        # zero,  and get  the difference  there -  this would  work with
        # variable  sampling rates  provided  the  different rates  were
        # integer  multiples.  another  trick is  to try  a power  of 10
        # times an  integer. (which  is now  implemented in  the calling
        # routine)

        # Apr 2010 - fixed bug for len(diff_sort) == 1 +1 in four places
        # like [0:last_small_diff_diffs_ind+1] - actually a bug for all,
        # only obvious for len(diff_sort) == 1
        deltar = np.mean(diff_sort[0:last_small_diff_diffs_ind + 1])

    iarr = (0.5 + (arr - np.min(arr)) / deltar).astype('i')
    remain = iarr - ((arr - np.min(arr)) / deltar)

    # remain is  relative to unit  step, need  to scale back  down, over
    # whole array
    maxerr = np.max(abs(remain)) * deltar / np.max(arr)

    # not clear what the max expected error is - small for 12 bits, gets
    # larger quicly

    # only use unsigned ints if we are NOT delta_encoding and signal >0
    if delta_encode is False and np.min(iarr) >= 0:
        if np.max(iarr) < 256:
            iarr = iarr.astype(np.uint8)

        elif np.max(iarr) < 16384:
            iarr = iarr.astype(np.uint16)

    else:
        if np.max(iarr) < 128:
            iarr = iarr.astype(np.int8)

        elif np.max(iarr) < 8192:
            iarr = iarr.astype(np.int16)

    ret_value = {'iarr': iarr, 'maxerror': maxerr, 'deltar': deltar,
                 'minarr': np.min(arr), 'intmax': np.max(iarr)}
    return ret_value


def find_subclasses(module, requested_class):
    subclasses = []
    for name, class_ in inspect.getmembers(module):
        if inspect.isclass(class_) and issubclass(class_, requested_class) and class_ != BaseBackendShotManager:
            subclasses.append(class_)
    return subclasses


def get_backend_shot_manager(tree):
    data_backend_module = tree.get_backend_module()
    candidate_classes = find_subclasses(data_backend_module, BaseBackendShotManager)
    if len(candidate_classes) == 1:
        return candidate_classes[0]
    if len(candidate_classes) == 0:
        msg = "Data backend module {} does not contain a subclass of BaseBackendShotManager".format(
            data_backend_module)
    else:
        msg = "Data backend module {} contains multiple subclasses of BaseBackendShotManager".format(
            data_backend_module)
    raise ImportError(msg)
