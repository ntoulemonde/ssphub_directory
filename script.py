from ssphub_directory.my_functions import *

remove_files_dir('ssphub/project/test')

fill_all_templates_from_grist('ssphub_directory/template.qmd', directory='ssphub/')

fill_template('ssphub_directory/template.qmd', get_grist_merge_as_df(), directory_output='ssphub')