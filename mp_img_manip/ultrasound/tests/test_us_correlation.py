import numpy as np
import scipy.signal as sig
import mp_img_manip.ultrasound.correlation as corr
import pytest


@pytest.fixture(scope='module')
def rand_array():
    array = np.random.randn(3, 4, 5)
    return array


class TestDetrend(object):
    def test_detrend_axis_0(self):
        array_dummy = rand_array()
        array_detrend = sig.detrend(array_dummy, 0)

        array_from_func = corr.detrend_along_dimension(array_dummy, dim_detrend=0)
        assert (array_detrend == array_from_func).all()

#
# class TestDetrendAndSubtractMean(object):
#     def test_detrend_axis_0_1(self):
#         array_dummy = np.random.randn(3, 4, 5)
#         array_detrend = sig.detrend(array_dummy, 0)
#         array_looped = np.zeros([3, 4, 5])
#         array_mean = np.mean(array_detrend, 1)
#         for i in range(4):
#             array_looped[:, i, :] = array_detrend[:, i, :] - array_mean
#
#         array_from_func = corr.detrend_along_dimension_and_subtract_mean(array_dummy, dim_detrend=0, dim_to_average=1)
#         assert (array_mean == array_from_func).all()
#
#     def test_detrend_axis_0_2(self):
#         array_dummy = np.random.randn(3, 4, 5)
#         array_detrend = sig.detrend(array_dummy, 0)
#         array_looped = np.zeros([3, 4, 5])
#         array_mean = np.mean(array_detrend, 2)
#         for i in range(5):
#             array_looped[:, :, i] = array_detrend[:, :, i] - array_mean
#
#         array_from_func = corr.detrend_along_dimension_and_subtract_mean(array_dummy, dim_detrend=0, dim_to_average=1)
#         assert (array_mean == array_from_func).all()
#
#     def test_detrend_axis_1_0(self):
#         array_dummy = np.random.randn(3, 4, 5)
#         array_detrend = sig.detrend(array_dummy, 1)
#         array_looped = np.zeros([3, 4, 5])
#         array_mean = np.mean(array_detrend, 1)
#         for i in range(4):
#             array_looped[:, i, :] = array_detrend[:, i, :] - array_mean
#
#         array_from_func = corr.detrend_along_dimension_and_subtract_mean(array_dummy, dim_detrend=0, dim_to_average=1)
#         assert (array_mean == array_from_func).all()
#
#     def test_detrend_axis_1_2(self):
#         array_dummy = np.random.randn(3, 4, 5)
#         array_detrend = sig.detrend(array_dummy, 2)
#         array_looped = np.zeros([3, 4, 5])
#         array_mean = np.mean(array_detrend, 1)
#         for i in range(4):
#             array_looped[:, i, :] = array_detrend[:, i, :] - array_mean
#
#         array_from_func = corr.detrend_along_dimension_and_subtract_mean(array_dummy, dim_detrend=0, dim_to_average=1)
#         assert (array_mean == array_from_func).all()
#
#     def test_detrend_axis_2_0(self):
#         array_dummy = np.random.randn(3, 4, 5)
#         array_detrend = sig.detrend(array_dummy, 2)
#         array_looped = np.zeros([3, 4, 5])
#         array_mean = np.mean(array_detrend, 1)
#         for i in range(4):
#             array_looped[:, i, :] = array_detrend[:, i, :] - array_mean
#
#         array_from_func = corr.detrend_along_dimension_and_subtract_mean(array_dummy, dim_detrend=0, dim_to_average=1)
#         assert (array_mean == array_from_func).all()
#
#     def test_detrend_axis_2_1(self):
#         array_dummy = np.random.randn(3, 4, 5)
#         array_detrend = sig.detrend(array_dummy, 2)
#         array_looped = np.zeros([3, 4, 5])
#         array_mean = np.mean(array_detrend, 1)
#         for i in range(4):
#             array_looped[:, i, :] = array_detrend[:, i, :] - array_mean
#
#         array_from_func = corr.detrend_along_dimension_and_subtract_mean(array_dummy, dim_detrend=0, dim_to_average=1)
#         assert (array_mean == array_from_func).all()
