import pytest
import SimpleITK as sitk
import multiscale.itk.registration as reg
import multiscale.utility_functions as util
import numpy as np


@pytest.fixture()
def user_input_fixture(monkeypatch):
        monkeypatch.setattr('builtins.input', lambda x: next(x))
        
        def _user_inputs(inputs):
                for item in inputs:
                        yield item
        
        return _user_inputs


class TestSetupSmoothingSigmas(object):
        @pytest.mark.parametrize('scale, expected', [
                (1, [0]), (2, [1, 0]), (4, [4, 2, 1, 0])
        ])
        def test_output_from_various_scales(self, scale, expected):
                output = reg._setup_smoothing_sigmas(scale)
                assert output == expected


class TestSetupShrinkFactors(object):
        @pytest.mark.parametrize('scale, expected', [
                (1, [1]), (4, [8, 4, 2, 1])
        ])
        def test_output_from_various_scales(self, scale, expected):
                output = reg._setup_shrink_factors(scale)
                assert output == expected
                

class TestSetRegistrationParametersDict(object):
        def test_default_parameters(self):
                expected = {
                        'scale': 1,
                        'iterations': 100,
                        'learning_rate': float(3),
                        'min_step': float(0.01),
                        'gradient_tolerance': float(1E-6),
                        'sampling_percentage': float(0.01),
                        'smoothing_sigmas': [0],
                        'shrink_factors': [1]
                }
                parameters = reg.setup_registration_parameters()
                assert expected == parameters

        def test_changed_parameters(self):
                expected = {
                        'scale': 3,
                        'iterations': 50,
                        'learning_rate': 0.5,
                        'min_step': 0.02,
                        'gradient_tolerance': 1E-5,
                        'sampling_percentage': 0.03,
                        'smoothing_sigmas': [2, 1, 0],
                        'shrink_factors': [3, 5, 1]
                }
                parameters = reg.setup_registration_parameters(scale=3, shrink_factors=[3, 5, 1],
                                                               iterations=50, learning_rate=0.5,
                                                               min_step=0.02, gradient_tolerance=1E-5,
                                                               sampling_percentage=0.03)
                assert expected == parameters

        def test_smoothing_sigmas_of_wrong_len_raises_error(self):
                with pytest.raises(ValueError):
                        params = reg.setup_registration_parameters(smoothing_sigmas=[4, 2])
                        
        def test_shrink_factors_of_wrong_len_raises_error(self):
                with pytest.raises(ValueError):
                        params = reg.setup_registration_parameters(shrink_factors=[4, 2])


class TestDefineRegistrationMethod(object):
        def test_function_returns_registration_method(self):
                parameters_dict = {
                        'scale': 2,
                        'iterations': 100,
                        'learning_rate': float(3),
                        'min_step': float(0.01),
                        'gradient_tolerance': float(1E-6),
                        'sampling_percentage': float(0.01)
                }
                registration_method = reg.define_registration_method(parameters_dict)
                assert type(registration_method) == sitk.ImageRegistrationMethod
                
                
class TestQueryRegistrationSamplingChange(object):
        # bug: Two registration methods that are made are automatically different.  These tests won't
        # work until there is a SimpleITK GetMetricSamplingPercentage test
        def test_sampling_changes_with_input(self, monkeypatch, user_input_fixture):
                unchanged_registration_method = sitk.ImageRegistrationMethod()
                changed_registration_method = sitk.ImageRegistrationMethod()
                
                monkeypatch.setattr('multiscale.utility_functions.query_yes_no', lambda x: True)
                monkeypatch.setattr('multiscale.utility_functions.query_float', lambda x: 0.5)
                
                reg.query_registration_sampling_change(changed_registration_method)
                assert unchanged_registration_method != changed_registration_method

        # def test_sampling_changes_correctly(self, monkeypatch, user_input_fixture):
        #         manually_changed_registration_method = sitk.ImageRegistrationMethod()
        #         manually_changed_registration_method.SetMetricSamplingPercentage(0.5)
        #
        #         changed_registration_method = sitk.ImageRegistrationMethod()
        #
        #         monkeypatch.setattr('multiscale.utility_functions.query_yes_no', lambda x: True)
        #         monkeypatch.setattr('multiscale.utility_functions.query_float', lambda x: 0.5)
        #
        #         reg.query_registration_sampling_change(changed_registration_method)
        #         assert manually_changed_registration_method == changed_registration_method


class TestQueryForChanges(object):
        def test_no_changes(self, monkeypatch):
                monkeypatch.setattr('multiscale.utility_functions.query_yes_no', lambda x: False)
                monkeypatch.setattr('multiscale.itk.itk_plotting.plot_overlay', lambda x, y, z: False)
                fixed_img = sitk.Image()
                moving_img = sitk.Image()
                initial_transform = sitk.AffineTransform(2)
                registration_method = sitk.ImageRegistrationMethod()
                
                fixed, moving, extracted = reg.query_for_changes(fixed_img, moving_img, initial_transform,
                                                                 registration_method)
                
                assert fixed is fixed_img
                assert moving is moving_img
                assert extracted is False
                