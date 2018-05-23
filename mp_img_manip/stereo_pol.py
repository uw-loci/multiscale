import python-bioformats as bf

def process_czi_file(czi_file_path, flat_field_path):

    czi_file_stacks = bf.open(czi_file_path)

    stage_position_list = []

    for stack in czi_file_stacks:
        stage_position_list.append(get_stage_position(stack))

        stack_intensity_corrected = correct_intensity(stack, flat_field_path)

        save_new_stack(stack_intensity_corrected)

    format_positions_for_stitching(stage_position_list)


def get_stage_position(stack):

def correct_intensity(stack, flat_field_path):


def format_positions_for_stitching(stage_position_list):


