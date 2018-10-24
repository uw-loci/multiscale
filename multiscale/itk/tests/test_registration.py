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


class TestSetRegistrationParametersDict(object):
        def test_default_parameters(self):
                expected = {
                        'scale': 1,
                        'iterations': 100,
                        'learning_rate': float(3),
                        'min_step': float(0.01),
                        'gradient_tolerance': float(1E-6),
                        'sampling_percentage': float(0.01)
                }
                parameters = reg.setup_registration_parameters()
                assert expected == parameters

        def test_changed_parameters(self):
                expected = {
                        'scale': 5,
                        'iterations': 50,
                        'learning_rate': 0.5,
                        'min_step': 0.02,
                        'gradient_tolerance': 1E-5,
                        'sampling_percentage': 0.03
                }
                parameters = reg.setup_registration_parameters(scale=5, iterations=50, learning_rate=0.5,
                                                               min_step=0.02, gradient_tolerance=1E-5,
                                                               sampling_percentage=0.03)
                assert expected == parameters


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