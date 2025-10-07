from ssphub_directory.my_functions import *

path='test/'
if os.path.exists(path):
        shutil.rmtree(path)

fill_all_templates_from_grist('ssphub_directory/template.qmd', directory='ssphub/')