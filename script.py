import ssphub_directory.my_functions  as my_f
import importlib
importlib.reload(my_f)  # When functions are updated

# To generate email
# generate_email(20, 'main', 'Infolettre de rentrée', get_emails())

# To generate template
# my_f.remove_files_dir('ssphub/project/test')
# my_f.fill_all_templates_from_grist()

# my_f.fill_all_templates_from_grist('ssphub_directory/template.qmd', directory='ssphub/project')

