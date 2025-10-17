import ssphub_directory.my_functions  as my_f
import importlib  # To reload package
importlib.reload(my_f)  # When functions are updated
import os

# To generate email
newsletter_nb = 20
## Validation
my_f.generate_email(
    newsletter_nb,
    'newsletter_'+str(newsletter_nb),
    "Pour validation - infolettre d'octobre du SSPHub",
    os.environ['EMAIL_VALIDATION_TO'],
    email_bcc='',
    email_from=None,
    email_cc=os.environ['EMAIL_VALIDATION_CC']+";"+os.environ['EMAIL_SSPHUB'])
## Send to all
my_f.generate_email(newsletter_nb, 'main', 'Infolettre de rentrée', get_emails())

# To generate template
# my_f.remove_files_dir('ssphub/project/test')
# my_f.fill_all_templates_from_grist()

# my_f.fill_all_templates_from_grist('ssphub_directory/template.qmd', directory='ssphub/project')

