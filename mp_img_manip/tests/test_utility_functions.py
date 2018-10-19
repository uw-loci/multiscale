import pytest
import mp_img_manip.utility_functions as util


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
                ('a', True),
                ('b', False),
                ('b.tif', False),
                ({'Test': 'Dict'}, False)
        ])
        def test_item_present(self, list_of_file_lists, item, expected):
                assert util.item_present_all_lists(item, list_of_file_lists) == expected

