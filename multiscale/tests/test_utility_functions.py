import pytest
import multiscale.utility_functions as util
import json
from pathlib import Path
import os
import numpy as np


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

@pytest.fixture()
def text_files_in_directory(tmpdir):
        txt_a = Path(tmpdir.join('a.txt'))
        txt_b = Path(tmpdir.join('b.txt'))
        txt_c = Path(tmpdir.mkdir('sub').join('c.txt'))
        txt_a.write_text('a')
        txt_b.write_text('b')
        txt_c.write_text('c')

        return txt_a, txt_b, txt_c


class TestWriteJSON(object):
        def test_write_object(self, tmpdir):
                content = {'test': 5, 'this': 'a', 'set': [1, 3], 'of': {'elements': 'please'}}
                json_path = tmpdir.join('test.json')
                util.write_json(content, json_path)
                with open(str(json_path), 'r') as file:
                        printed_content = json.load(file)
                        assert printed_content == content

        def test_tuple_writes_as_list(self, tmpdir):
                content = {'tuple': (5, 4, 3)}
                json_path = tmpdir.join('tuple_test.json')
                util.write_json(content, json_path)
                with open(str(json_path), 'r') as file:
                        printed = json.load(file)
                        assert printed == {'tuple': [5, 4, 3]}


class TestReadJSON(object):
        @pytest.mark.parametrize('file_content, expected', [
                ({"Test": "Value"}, {'Test': 'Value'})
        ])
        def test_read_string_io(self, tmpdir, file_content, expected):
                path = tmpdir.join('test.json')
                with open(str(path), 'w') as file:
                        json.dump(file_content, file)
                output = util.read_json(path)
                assert output == expected


class TestMoveFilesToNewFolder(object):
        @pytest.fixture()
        def list_files(self, tmpdir):
                files = [tmpdir.join('Test.txt'), tmpdir.join('Test2.json')]
                return files

        def test_move_files_existing_folder(self, list_files, tmpdir):
                files = list_files
                for file in files:
                        file.write('Hello')

                file_paths = [Path(file) for file in files]
                file_names = [file.name for file in file_paths]
                new_dir = tmpdir.mkdir('test_folder')
                util.move_files_to_new_folder(file_paths, new_dir)
                for file in file_names:
                        assert file in os.listdir(new_dir)

        def test_move_files_to_new_folder(self, list_files, tmpdir):
                files = list_files
                for file in files:
                        file.write('Hello')

                file_paths = [Path(file) for file in files]
                file_names = [file.name for file in file_paths]
                new_dir = Path(tmpdir, 'test_folder')
                util.move_files_to_new_folder(file_paths, new_dir)
                for file in file_names:
                        assert file in os.listdir(new_dir)


class TestItemPresentAllLists(object):
        @pytest.mark.parametrize("item, expected", [
                ('a', True), ('b', False), ('b.tif', False), ({'Test': 'Dict'}, False)
        ])
        def test_item_present(self, list_of_file_lists, item, expected):
                assert util.item_present_all_lists(item, list_of_file_lists) == expected


class TestListFiletypeInDir(object):
        def test_finds_text_file_types_in_dir(self, tmpdir, text_files_in_directory):
                all_files = text_files_in_directory
                expected = [all_files[0], all_files[1]]
                found = util.list_filetype_in_dir(Path(tmpdir), '.txt')
                assert found == expected


class TestListFiletypeInSubdir(object):
        def test_finds_text_file_types_in_dir(self, tmpdir, text_files_in_directory):
                all_files = text_files_in_directory
                expected = [file for file in all_files]
                found = util.list_filetype_in_subdirs(Path(tmpdir), '.txt')
                assert found == expected


class TestQueryInt(object):
        def test_user_gives_int(self, monkeypatch):
                monkeypatch.setattr('builtins.input', lambda x: '5')
                assert util.query_int('') == 5
                
        def test_user_gives_wrong_inputs_then_int(self, user_input_fixture):
                user_inputs = user_input_fixture(['5.4', 'eight', 'a5', '5a', '5'])
                assert util.query_int(user_inputs) == 5
                

class TestQueryFloat(object):
        def test_user_gives_float(self, monkeypatch):
                monkeypatch.setattr('builtins.input', lambda x: '5.4')
                assert util.query_float('') == 5.4
        
        def test_user_gives_int(self, monkeypatch):
                monkeypatch.setattr('builtins.input', lambda x: '5')
                assert util.query_float('') == 5.0

        def test_user_gives_wrong_inputs_then_float(self, user_input_fixture):
                user_inputs = user_input_fixture(['eight', 'a5', '5a', '5.4'])
                assert util.query_float(user_inputs) == 5.4


class TestQueryStr(object):
        @pytest.mark.parametrize('input', [
                ('a'), ('\u0394'), ('4.52')
        ])
        def test_some_forms_of_input(self, monkeypatch, input):
                monkeypatch.setattr('builtins.input', lambda x: input)
                output = util.query_str(input)
                assert input == output


class TestQueryYesNo(object):
        @pytest.mark.parametrize("input, expected", [
                ('YES', True),('Y', True),  ('YE', True),('yes', True),('y', True),('ye', True),
                ('NO', False),('N', False),('n', False),('no', False)
        ])
        def test_yes_no_inputs(self, input, expected, monkeypatch):
                monkeypatch.setattr('builtins.input', lambda x: input)
                assert util.query_yes_no('') is expected
        
        def test_bad_input_then_yes(self, monkeypatch, user_input_fixture):
                user_inputs = user_input_fixture(['5', 'y', 'test'])
                assert util.query_yes_no(user_inputs) is True


class TestCharacterIndices(object):
        @pytest.mark.parametrize('string, character, indices', [
                ('aabcda', 'a', [0, 1, 5]), #regular character
                ('z12dc1', '1', [1, 5]), #number
                ('aa\ndc', '\n', [2]), #tab character
                ('dd\u0061adc', 'a', [2, 3]), #unicode regular character
                ('abc\u0394d\u0394', '\u0394', [3, 5]) #unicode special character
        ])
        def test_find_char(self, string, character, indices):
                result = util.character_indices(string, character)
                assert result == indices


class TestQueryStrList(object):
        def test_a_bunch_of_strs(self, user_input_fixture, monkeypatch):
                user_inputs = ['a', 'b', 'c']
                generator = user_input_fixture(user_inputs)
                monkeypatch.setattr('builtins.input', lambda x: next(generator))
                output = util.query_str_list(['First letter', 'second', 'third'])
                assert output == user_inputs


class TestQueryFloatList(object):
        def test_a_bunch_of_Floats(self, user_input_fixture, monkeypatch):
                user_inputs = ['0.1', '0.2', '0.3']
                generator = user_input_fixture(user_inputs)
                monkeypatch.setattr('builtins.input', lambda x: next(generator))
                output = util.query_str_list(['First', 'second', 'third'])
                assert output == user_inputs


class TestSplitListIntoSublists(object):
        @pytest.mark.parametrize('large_list, size, expected', [
                (['a']*10, 3, [['a']*3, ['a']*3, ['a']*3, ['a']]),
                ([4]*4, 2, [[4]*2, [4]*2])
        ])
        def test_list_returns_sublists_of_correct_sizes(self, large_list, size, expected):
                list_len = len(large_list)
                num_lists = int(np.ceil(list_len/size))

                sublists = util.split_list_into_sublists(large_list, size)

                for list_num in range(num_lists):
                        assert next(sublists) == expected[list_num]
