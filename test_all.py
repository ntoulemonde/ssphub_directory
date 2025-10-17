from ssphub_directory.my_functions import *

def test_generate_email():
    generate_email(19, 'main', 'Infolettre de rentrée', 'my_to_email@insee.fr', get_emails())

def test_extract_emails():

    # writing testing file
    lines = [
        'test1@example.com\n',  # Email alone
        'Contact me at test2@example.com for more information.\n',  # Email in the middle of a sentence
        'This is a normal line of text.\n',  # Normal line
        'Email: test3@example.com\n',  # Email alone with label
        'Please send your feedback to test4@example.com.\n',  # Email in the middle of a sentence
        'Another normal line of text.\n',  # Normal line
        'test5@example.com\n',  # Email alone
        'You can reach me at test6@example.com if you have any questions.\n',  # Email in the middle of a sentence
        'Yet another normal line of text.\n',  # Normal line
        'Email address: test7@example.com\n',  # Email alone with label
        'Contact us at test8@example.com for support.\n',  # Email in the middle of a sentence
        'More normal text here.\n',  # Normal line
        'test9@example.com\n',  # Email alone
        'Please email your inquiries to test10@example.com.\n',  # Email in the middle of a sentence
        'Still normal text.\n',  # Normal line
        'Email: test1@example.com\n',  # Email alone with label
        'You can find more details at test2@example.com.\n',  # Email in the middle of a sentence
        'Normal text continues.\n',  # Normal line
        'test3@example.com\n',  # Email alone
        'Contact me at test4@example.com for assistance.\n'  # Email in the middle of a sentence
    ]

    with open('ssphub_directory/test/replies.txt', mode='w') as file:
        file.writelines(lines)

    # Test function
    assert "test9@example.com" in extract_emails_from_txt(file_path='ssphub_directory/test/replies.txt')
    
# def test_export_list_to_csv():
#     export_list_to_csv(extract_emails_from_txt(), 'output/temp.csv')

def test_fill_template_one_row():
    # Create a test DataFrame with the variables to replace
    df = pd.DataFrame({
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
        'my_table_repo_path': ['- [here](https://www.google.com/) <br>- or [here](https://www.google.com/)'], 
        'nom_dossier': ['test/mytest']
    })

    fill_template('ssphub_directory/template.qmd', df, 'ssphub_directory/')


def test_fill_template_two_rows():
    new_website_df = get_grist_merge_as_df()  
    fill_template('ssphub_directory/template.qmd', new_website_df.head(2), 'ssphub_directory/')


def test_website_merge():
    # df = get_website_merge_as_df().head(1)
    df = get_grist_merge_as_df()
    fill_template('ssphub_directory/template.qmd', df)


def test_update_polars():
    print(get_directory_as_df())

def test_update_polars2():
    get_emails()


def test_grist_attachment_download():
    url = get_grist_attachments_config()[0]
    headers = get_grist_attachments_config()[1]

    download_file(url, output_dir='.temp/', headers=headers)
    unzip_dir('.temp/Fusion_site_SSPHub-Attachments.zip', '.temp/extracted_data')


def test_global():
    remove_files_dir('.temp/', 'ssphub_directory/test/', 'test/')
    
    fill_all_templates_from_grist(directory='ssphub_directory/test')
    generate_email(19, 'main', 'Infolettre de rentrée', 'my_to_email@insee.fr', get_emails())