import ssphub_directory.my_functions  as my_f
import importlib
importlib.reload(my_f)  # When functions are updated

my_f.remove_files_dir('ssphub/project/test')
my_f.remove_files_dir('ssphub_directory/project')

my_f.fill_all_templates_from_grist()

my_f.fill_all_templates_from_grist('ssphub_directory/template.qmd', directory='ssphub/project')

my_f.fill_template('ssphub_directory/template.qmd', get_grist_merge_as_df(), directory_output='ssphub')