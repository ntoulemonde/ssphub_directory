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

# Create a test DataFrame with the variables to replace
test_data = pd.DataFrame({
    'my_title': ['Title test'],
    'my_description': ['Description test'],
    'my_authors': ['- John \n- Jackie'],
    'my_date': ['2023-10-01'],
    'my_image_path': ['/path/to/image.jpg'],
    'my_categories': ['- Category1 \n- Category2'],
    'my_table_title': ['Table Title test'],
    'my_table_details': ['Table Details test'],
    'my_table_sponsor': ['Sponsor Name test'],
    'my_table_team': ['- John <br> - Jackie'],
    'my_table_contact': ['Contact Info test'],
    'my_table_results': ['- I have several results available [here](https://www.google.com/) <br> - and another one [here](https://www.qwant.fr)'],
    'my_table_repo_path': ['- [here](https://www.google.com/) <br>- or [here](https://www.google.com/)']
})


with open('ssphub_directory/model.qmd', 'r') as model_file:
    model_content = model_file.read()

for index, row in test_data.iterrows():
    for column in test_data.columns:
        variable_name = column
        variable_value = row[column]
        print('{{'+ variable_name + '}} : ' + str(variable_value))
        model_content = model_content.replace('{{'+ variable_name + '}}', str(variable_value))

model_content

with open('ssphub_directory/res.qmd', 'w') as res_file:
    res_file.write(model_content)