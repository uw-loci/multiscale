import pytest
import SimpleITK as sitk
import multiscale.itk.registration as reg
import multiscale.utility_functions as util


@pytest.fixture()
def user_input_fixture(monkeypatch):
        monkeypatch.setattr('builtins.input', lambda x: next(x))
        
        def _user_inputs(inputs):
                for item in inputs:
                        yield item
        
        return _user_inputs


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