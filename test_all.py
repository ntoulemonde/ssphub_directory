from ssphub_directory.my_functions import *


def test_generate_email():
    generate_email(19, 'main', 'Infolettre de rentrée', get_emails())

def test_extract_emails():
    assert "nicolas.toulemonde@insee.fr" in extract_emails()
    
# def test_export_list_to_csv():
#     export_list_to_csv(extract_emails(), 'output/temp.csv')

def test_fill_template():
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
        'my_table_actors': ['- John <br> - Jackie'],
        'my_table_contact': ['Contact Info test'],
        'my_table_results': ['- I have several results available [here](https://www.google.com/) <br> - and another one [here](https://www.qwant.fr)'],
        'my_table_repo_path': ['- [here](https://www.google.com/) <br>- or [here](https://www.google.com/)']
    })
    
    fill_template('ssphub_directory/template.qmd', test_data, 'ssphub_directory/test/mon_modele.qmd')

def test_website_merge():
    # df = get_website_merge_as_df().head(1)
    df = get_website_merge_as_df()
    fill_template('ssphub_directory/template.qmd', df)

