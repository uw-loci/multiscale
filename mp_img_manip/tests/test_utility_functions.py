import pytest
import mp_img_manip.utility_functions as util


@pytest.fixture()
def user_input_fixture(monkeypatch):
        monkeypatch.setattr('builtins.input', lambda x: next(x))
        def _user_inputs(inputs):
                for item in inputs:
                        yield item
                
        return _user_inputs

@pytest.fixture()
def list_of_file_lists():
        """
        Returns a list of file lists containing lists for different conditions
        :return:
        """
        list_one = ['a', 'b.tif', 'c.png', 'd']
        list_two = ['a', 'b.tif', 'c.test']
        list_three =['a', 'b', 'c.tif', {'Test': 'Dict'}]
        lists = [list_one, list_two, list_three]
        return lists


class TestItemPresentAllLists(object):
        @pytest.mark.parametrize("item, expected", [
                ('a', True), ('b', False), ('b.tif', False), ({'Test': 'Dict'}, False)
        ])
        def test_item_present(self, list_of_file_lists, item, expected):
                assert util.item_present_all_lists(item, list_of_file_lists) == expected


class TestQueryInt(object):
        def test_user_gives_int(self, monkeypatch):
                monkeypatch.setattr('builtins.input', lambda x: '5')
                assert util.query_int('') == 5
                
        def test_user_gives_wrong_inputs_then_int(self, monkeypatch, user_input_fixture):
                user_inputs = user_input_fixture(['5.4', 'eight', 'a5', '5a', '5'])
                assert util.query_int(user_inputs) == 5
                

class TestQueryFloat(object):
        def test_user_gives_float(self, monkeypatch):
                monkeypatch.setattr('builtins.input', lambda x: '5.4')
                assert util.query_float('') == 5.4
        
        def test_user_gives_int(self, monkeypatch):
                monkeypatch.setattr('builtins.input', lambda x: '5')
                assert util.query_float('') == 5.0

        def test_user_gives_wrong_inputs_then_float(self, monkeypatch, user_input_fixture):
                user_inputs = user_input_fixture(['eight', 'a5', '5a', '5.4'])
                assert util.query_float(user_inputs) == 5.4
                

class TestYesNo(object):
        @pytest.mark.parametrize("input, expected", [
                ('YES', True),('Y', True),  ('YE', True),('yes', True),('y', True),('ye', True),
                ('NO', False),('N', False),('n', False),('no', False)
        ])
        def test_yes_no_inputs(self, input, expected, monkeypatch):
                monkeypatch.setattr('builtins.input', lambda x: input)
                assert util.yes_no('') == expected
        
        def test_bad_input_then_yes(self, monkeypatch, user_input_fixture):
                user_inputs = user_input_fixture(['5', 'y', 'test'])
                assert util.yes_no(user_inputs) == True