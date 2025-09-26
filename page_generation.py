# Dic
# my_title  # Title of the webpage
# my_description
# my_authors
# my_date
# my_image_path
# my_categories
# my_table_title 
# my_table_details
# my_table_sponsor
# my_table_team
# my_table_contact
# my_table_results
# my_table_repo_path

import pandas as pd
import os
from grist_api import GristDocAPI  # To get directory emails

def ensure_folders_exist(file_path):
    """
    Ensure that every folder in the given file path exists. If any folder is missing, create it.

    Args:
        file_path (str): The file path to check and create folders for.
    """
    # Normalize the path to handle any relative path components
    normalized_path = os.path.normpath(file_path)

    # Split the path into its components
    path_components = normalized_path.split(os.sep)
   
    # Remove the last component if it is a file
    if '.' in path_components[-1]:
        path_components = path_components[:-1]

    # Initialize the current path
    current_path = path_components[0]

    # Iterate over the path components
    for component in path_components[1:]:
        # Update the current path
        current_path = os.path.join(current_path, component)

        # Check if the current path is a directory
        if not os.path.isdir(current_path):
            # Create the directory if it does not exist
            os.makedirs(current_path)
            print(f"Created directory: {current_path}")


def replace_model(path_to_model, df, path_to_output=None):
    with open(path_to_model, 'r') as model_file:
        model_content = model_file.read()

    for index, row in df.iterrows():
        for column in df.columns:
            variable_name = column
            variable_value = row[column]
            print('{{'+ variable_name + '}} : ' + str(variable_value))
            model_content = model_content.replace('{{'+ variable_name + '}}', str(variable_value))

    if path_to_output is not None:
        ensure_folders_exist(path_to_output)
        with open(path_to_output, 'w') as res_file:
            res_file.write(model_content)

    return model_content


# Create a test DataFrame with the variables to replace
# test_data = pd.DataFrame({
#     'my_title': ['Title test'],
#     'my_description': ['Description test'],
#     'my_authors': ['- John \n- Jackie'],
#     'my_date': ['2023-10-01'],
#     'my_image_path': ['/path/to/image.jpg'],
#     'my_categories': ['- Category1 \n- Category2'],
#     'my_table_title': ['Table Title test'],
#     'my_table_details': ['Table Details test'],
#     'my_table_sponsor': ['Sponsor Name test'],
#     'my_table_team': ['- John <br> - Jackie'],
#     'my_table_contact': ['Contact Info test'],
#     'my_table_results': ['- I have several results available [here](https://www.google.com/) <br> - and another one [here](https://www.qwant.fr)'],
#     'my_table_repo_path': ['- [here](https://www.google.com/) <br>- or [here](https://www.google.com/)']
# })

# replace_model('ssphub_directory/model.qmd', test_data, 'ssphub_directory/hi/mon_model.qmd')

def get_api_website_login():
    # Log in to GRIST API
    SERVER = "https://grist.numerique.gouv.fr/"
    DOC_ID = os.environ['SSPHUB_WEBSITE_MERGE_ID']
    os.environ['GRIST_API_KEY'] = os.environ['MY_GRIST_API_KEY']

    # Returning API details connection
    return GristDocAPI(DOC_ID, server=SERVER)

# Get API table
def get_website_merge_as_df():
    # fetch all the rows
    api_merge = get_api_website_login()
    new_website_df = api_merge.fetch_table('Intranet_details')
    new_website_df = pd.DataFrame(new_website_df)
    print(new_website_df['id'].nunique())

    # Selecting useful columns
    cols_to_keep = ['id', 'Titre', 'Sponsor', 'Equipe', 'Point_de_contact',
       'Resultats', 'Details_du_projet', 'sous_titre', 'auteurs',
       'Code_du_projet', 'tags', 'nom_dossier', 'date',
       'image']

    return new_website_df[cols_to_keep]


get_website_merge_as_df().columns

variable_mapping = {
        'Titre': 'my_title',
        'sous_titre': 'my_description',
        'auteurs': 'my_authors',
        'date': 'my_date',
        'image': 'my_image_path',
        'tags': 'my_categories',
        'Titre': 'my_table_title',
        'Details_du_projet': 'my_table_details',
        'Sponsor': 'my_table_sponsor',
        'Equipe': 'my_table_team',
        'Point_de_contact': 'my_table_contact',
        'Resultats': 'my_table_results',
        'Code_du_projet': 'my_table_repo_path'
}