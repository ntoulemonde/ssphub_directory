# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "email-mime",
#     "os",
#     "pyyaml",
#     "requests",
#     "grist-api",
#     "pandas",
# ]
# ///

from email.mime.multipart import MIMEMultipart  # To generate the draft email
from email.mime.text import MIMEText  # To generate the draft email
import requests  # To transform newsletter into email, call Github API and download files
import yaml  # To update newsletter qmd metadata for the email
import os  # to remove temporary files, create directory etc
from grist_api import GristDocAPI  # To get directory emails
import polars as pl  # to manage directory emails
import pandas as pd  # to manage directory emails
import csv  # to store results of data cleaning
import re  # For pattern matching to search for emails
import shutil  # to remove directory and its content
import zipfile  # GRIST attachments

def generate_eml_file(email_body, subject, bcc_recipient, to_recipient=":DG75-SSPHUB-Contact <SSPHUB-contact@insee.fr>"):
    """
    Creates an .eml file and saves it to .temp/email.eml

    Args:
        email_body (string): html body of the email
        subject (string): Object of the email
        bcc_recipient (string): list of recipients of the emails. 
        to_recipient (string): Email of the sender to indicate (be cautious, it doesn't automate the sending)

    Returns:
        None
    Nb : create the email to .temp/email.eml with a message

    Example:
        >>> generate_eml_file('body', 'this an email', 'test@test.fr')
    Email saved as .temp/email.eml
    """
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['BCC'] = bcc_recipient
    msg['To'] = to_recipient   # Auto send the email
    msg['From'] = 'SELECT THE RIGHT EMAIL'  # Set the sender's email address
    msg['X-Unsent'] = '1'  # Mark the email as unsent : when the file is opened, it can be sent.

    # Attach the HTML body
    msg.attach(MIMEText(email_body, 'html'))

    # Save the email as an .eml file
    eml_file_path = '.temp/email.eml'

    # Create the output directory if it doesn't exist
    os.makedirs('.temp', exist_ok=True)

    with open(eml_file_path, 'wb') as f:
        f.write(msg.as_bytes())

    print(f"Email saved as {eml_file_path}")


def fetch_qmd_file(url):
    """
    get the qmf file from an url and return it as string

    Args:
        url (string): the qmd url to fetch. Usually a github raw URL

    Returns:
        (string) the text of the qmd file

    Example:
        >>> fetch_qmd_file('https://raw.githubusercontent.com/InseeFrLab/ssphub/refs/heads/main/infolettre/infolettre_19/index.qmd')
    '---\ntitle: "La rentrée 2025: actualités, nouveautés, interview de rentrée"\n\ndescription: |\n  Infolettre du mois de 
    __Septembre 2025__\n\n# Date published\ndate: \'2025-09-29\'\nnumber: 19\n\nauthors:\n ......'
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the .qmd file: {e}")
        return None


def process_qmd_file(qmd_content, qmd_output_file, newsletter_url='https://ssphub.netlify.app/infolettre/'):
    """
    Transform a newsletter qmd file to a qmd file that will be knitted by
    calling the function to transform the yaml part of the qmd file

    Args:
        qmd_content (string): the original qmd file to process, typically the result of fetch_qmd_file
        qmd_output_file (string): the path of the qmd file to write
        newsletter_url (string): to pass the argument onto yaml to insert link to newsletter

    Returns:
        None
    Nb : writes the processed qmd file

    Example:
        >>> process_qmd_file(
    fetch_qmd_file('https://raw.githubusercontent.com/InseeFrLab/ssphub/refs/heads/main/infolettre/infolettre_19/index.qmd'),
    'cleaned_index.qmd')
    """

    # qmd_content = fetch_qmd_file('https://raw.githubusercontent.com/InseeFrLab/ssphub/refs/heads/main/infolettre/infolettre_19/index.qmd')
    # Split the YAML header and the HTML content
    parts = qmd_content.split('---', 2)
    if len(parts) < 3:
        print("Invalid .qmd file format")
        return None

    yaml_header = parts[1]
    html_content = parts[2]

    # Clean the YAML header
    cleaned_yaml_header = clean_yaml_header(yaml_header, newsletter_url)

    # Combine the cleaned YAML header and HTML content
    processed_qmd_content = f"---\n{cleaned_yaml_header}---\n{html_content}"

    # Save the processed QMD content to a file
    with open(qmd_output_file, 'w', encoding='utf-8') as f:
        f.write(processed_qmd_content)


def clean_yaml_header(yaml_header, newsletter_url):
    """
    Function to transform Yaml header of an index.qmd file and transform it for a qmd file that will be
    knitted to html. It keeps only title, updates the description with the link to the website, 
    add lang, format and format options, including a css file.

    Arg :
        yaml_header: input yaml_header to clean, as string
        newsletter_url: url of the newsletter to insert a link to that newsletter

    Returns:
        (string, with Unicode formating) url to raw Qmd newsletter

    Example:
        >>> clean_yaml_header(
            '\ntitle: "La rentrée 2025:"\n\ndescription: |\n  Infolettre de __Septembre 2025__
            \n\n# Date published\ndate: \'2025-09-29\'\nnumber: 19\n\nauthors:\n  - Nicolas\n\nimage: mage.png\n\ntags:\n
            - datavis\n  - IA \n\ncategories:\n  - Infolettre\n\n',
            'https://ssphub.netlify.app/infolettre/'
            )
        "title: 'La rentrée 2025:'\ndescription: '*Infolettre de __Septembre 2025__ disponible sur le site du [réseau](https://ssphub.netlify.app/infolettre/)*'\nlang: fr\nformat:\n  html:\n    self-contained: true\n    css: ../ssphub_directory/email_style/style.css\n"

    """

    # Parse the YAML header1
    yaml_data = yaml.safe_load(yaml_header)

    # Keep only the specified keys
    # We put the link
    description = ("*" + yaml_data.get('description', '').strip() +
                " disponible sur le site du [réseau](" + newsletter_url + ")*"
                )

    cleaned_yaml = {
        'title': yaml_data.get('title', '').strip(),
        'description': description
                }

    # Add missing params
    cleaned_yaml['lang'] = 'fr'
    cleaned_yaml['format'] = {
        'html': {
            'self-contained': True,  # To have images inside the email
            'css': '../ssphub_directory/email_style/style.css'
            }
        }

    # Convert the cleaned YAML back to a string
    cleaned_yaml_str = yaml.dump(cleaned_yaml, sort_keys=False,  allow_unicode=True, width=4096)
    return cleaned_yaml_str


def knit_to_html(processed_qmd_file):
    """
    knit a qmd file to html 

    Args:
        processed_qmd_file (string): file path to the qmd file to knit

    Returns:
        None
    Saves the knitted file with same name as qmd file, same folder
    """
    # Use the Quarto CLI to knit the QMD file to HTML
    import subprocess
    try:
        subprocess.run(['quarto', 'render', processed_qmd_file, '--to', 'html'], check=True)
        print("QMD file successfully knitted to HTML")
    except subprocess.CalledProcessError as e:
        print(f"Error knitting QMD file to HTML: {e}")


def raw_url_newsletter(number, branch='main'):
    """
    Function to get url of raw Qmd files of a newsletter on SSPHub repo

    Arg :
        number: number of the newsletter
        branch: branch of the repo to look for

    Returns:
        (string) Url to raw Qmd newsletter
    """
    return f"https://raw.githubusercontent.com/InseeFrLab/ssphub/refs/heads/{branch}/infolettre/infolettre_{number}/index.qmd"


def published_url_newsletter(number):
    """
    Function to generate url of published newsletter on SSPHub website

    Arg :
        number: number of the newsletter

    Returns:
        url to ssphub website of the given newsletter
        Output format: a string

    Example:
        >>> published_url_newsletter('19')
        'https://ssphub.netlify.app/infolettre/infolettre_19/'
    """
    return f"https://ssphub.netlify.app/infolettre/infolettre_{number}/"


def list_raw_image_files(repo_owner, repo_name, subfolder_path, branch='main'):
    """
    List image files present in a given github folder. Images are defined by the following formats
    ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp')

    Arg :
        repo_owner : name of the owner of the repo in Github
        repo_name : name of the Github repo
        subfolder_path : in the given repo architecture, a subfolder path to the folder where you want to list all files.
    For example : infolettre/infolettre_19/
        branch where the newsletter is (main by default)

    Returns:
        url to the raw images files
        Output format: a list of strings

    Example:
        >>> list_raw_image_files('InseeFrLab', 'ssphub', 'infolettre/infolettre_19', branch='main')
        ['https://raw.githubusercontent.com/InseeFrLab/ssphub/refs/heads/main/infolettre/infolettre_19/2025_09_back_school.png',
        'https://raw.githubusercontent.com/InseeFrLab/ssphub/refs/heads/main/infolettre/infolettre_19/measles-cases-historical-us-states-heatmap.png']

    """
    # GitHub API URL to list contents of a subfolder
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{subfolder_path}?ref={branch}"

    try:
        # Send a GET request to the GitHub API
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the JSON response
        contents = response.json()

        # Filter image files (assuming common image extensions)
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'}
        image_files = [
            f'https://raw.githubusercontent.com/{repo_owner}/{repo_name}/refs/heads/{branch}/{item['path']}' for item in contents
            if item['type'] == 'file' and os.path.splitext(item['name'])[1].lower() in image_extensions
        ]

        return image_files
    except requests.exceptions.RequestException as e:
        print(f"Error fetching contents from GitHub API: {e}")
        return None


def list_image_files_for_newsletter(number, branch='main'):
    """
    Wrapper of list_raw_image_files. List image files present in the github folder InseeFrLab, repo ssphub. Ima

    Arg :
        number of the newsletter
        branch where the newsletter is (main by default)

    Returns:
        list of path to the raw images files

    Example:
        >>> list_image_files_for_newsletter('19', branch='main')
        ['https://raw.githubusercontent.com/InseeFrLab/ssphub/refs/heads/main/infolettre/infolettre_19/2025_09_back_school.png',
        'https://raw.githubusercontent.com/InseeFrLab/ssphub/refs/heads/main/infolettre/infolettre_19/measles-cases-historical-us-states-heatmap.png']

    """
    repo_owner = 'InseeFrLab'
    repo_name = 'ssphub'
    subfolder_path = f'infolettre/infolettre_{number}'

    return list_raw_image_files(repo_owner, repo_name, subfolder_path, branch)


def download_file(file_url, output_dir='.temp', headers=None):
    """
    Downloads a file from given url and store it in output_dir

    Arg:
        file_url: url of the file to download, as a string
        output_dir: directory where to save the file to, as a string

    Returns:
        nothing
        print if download was successfull

    Example:
        >>> download_file('https://raw.githubusercontent.com/InseeFrLab/ssphub/refs/heads/main/infolettre/infolettre_19/2025_09_back_school.png')
        File downloaded to .temp/2025_09_back_school.png
        """

    try:
        # Send a GET request to the GitHub API
        response = requests.get(file_url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Extract the file name from the response or, if not, from file_url
        if 'Content-Disposition' in response.headers:
            file_name = response.headers['Content-Disposition'].split('filename=')[-1].strip('"').replace(' ', '_')
        else:
            file_name = os.path.basename(file_url)

        # Save the file to the output directory
        output_path = os.path.join(output_dir, file_name)
        with open(output_path, 'wb') as f:
            f.write(response.content)

        print(f"File downloaded to {output_path}")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")


def unzip_dir(zip_file_path, extraction_dir):
    """
    Unzip a folder

    Args:
        zip_file_path (string): path to file to unzip.
        extraction_dir (string): path to directory to unzip files

    Result: 
        None. A message is printed. 
    
    Example:
        >>> unzip_dir('.temp/Fusion_site_SSPHub-Attachments.zip', '.temp/extracted_data')
        Files extracted to .temp/extracted_data
    """
    # Define the path to the zip file and the extraction directory
    # zip_file_path = '.temp/Fusion_site_SSPHub-Attachments.zip'
    # extraction_dir = '.temp/extracted_data'

    # Create the extraction directory if it doesn't exist
    if not os.path.exists(extraction_dir):
        os.makedirs(extraction_dir)

    # Open the zip file
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        # Extract all the contents into the specified directory
        zip_ref.extractall(extraction_dir)

    print(f"Files extracted to {extraction_dir}")


def rename_grist_attachments(dir_path):
    """
    Remove the first 42 characters of filenames in a folder. 
    Attachment from GRIST are named :
    'e5e7c83c9a7c795d5a2c2f45923b567b7be21232_visuel_Budget_des_familles(1).png'

    Args:
        dir_path (string): path to directory.

    Result:
        A list of the renamed files

    Example:
        >>> rename_grist_attachments('.temp/extracted_data')
    ['2025_09_back_school_old.jpg', 'visuel_Budget_des_familles(1).png', '2025_09_back_school.png',
    'visuel_Budget_des_familles.png']
    """
    # Removing the first part of the filename, a hash of 40 characters
    for file_name in os.listdir(dir_path):
        os.rename(dir_path + '/' + file_name, dir_path + '/' + file_name[41:])

    return os.listdir(dir_path)


def download_images_for_newsletter(number, branch='main', output_dir='.temp'):
    """
    Download all image files from given newsletter number and branch and store it in output_dir

    Arg:
        number: number of the newsletter whose images will be downloaded, as a string
        branch: repo branch of the newsletter (main for published newsletter, other for non published newsletters)
        output_dir: directory where to save the files to, as a string

    Returns:
        nothing
        nb : a message is printed if download was successfull

    Example:
        >>> download_file('https://raw.githubusercontent.com/InseeFrLab/ssphub/refs/heads/main/infolettre/infolettre_19/2025_09_back_school.png')
        Image file downloaded to .temp/2025_09_back_school.png
    """
    # Get the list of image files in the subfolder
    image_files = list_image_files_for_newsletter(number, branch)

    if not image_files:
        print("No image files found in the subfolder.")

    # Download each image file
    downloaded_files = []
    for image_file_url in image_files:
        downloaded_file = download_file(image_file_url, output_dir)
        if downloaded_file:
            downloaded_files.append(downloaded_file)

    return downloaded_files


def generate_email(number, branch, email_object, email_dest, drop_temp=True):
    """
    Generates the draft email for a newsletter in the folder '.temp/'. Built on previous functions.

    Arg:
        number (string): number of the newsletter to turn into email
        branch (string): repo branch of the newsletter to turn into email (main for published newsletter, other for non published newsletters)
        email_object (string): object of the email
        email_dest (string) : list of email adresses to send the email to.
        drop_temp (boolean): if temporary knitted files should be removed after knitting. Default is true

    Returns:
        None

    Example:
        >>> download_file('https://raw.githubusercontent.com/InseeFrLab/ssphub/refs/heads/main/infolettre/infolettre_19/2025_09_back_school.png')
        Image file downloaded to .temp/2025_09_back_school.png
    """
    temp_file = './.temp/temp'
    temp_file_qmd = temp_file + '.qmd'
    temp_file_html = temp_file + '.html'

    download_images_for_newsletter(number, branch, '.temp')

    qmd_content = fetch_qmd_file(raw_url_newsletter(number, branch))
    process_qmd_file(qmd_content, temp_file_qmd, published_url_newsletter(number))
    knit_to_html(temp_file_qmd)

    with open(temp_file_html, 'r', encoding="utf-8") as f:
        generate_eml_file(f.read(), email_object, email_dest)

    if drop_temp:
        os.remove(temp_file_qmd)
        os.remove(temp_file_html)


def get_grist_directory_login():
    """
    Send back GRIST API login details

    Args:
        None

    Returns:
        A GristDocAPI object
    """
    # Log in to GRIST API
    SERVER = "https://grist.numerique.gouv.fr/"
    DOC_ID = os.environ['SSPHUB_DIRECTORY_ID']

    if 'GRIST_API_KEY' not in os.environ:
        raise ValueError("The GRIST_API_KEY environment variable does not exist.")

    # Returning API details connection
    return GristDocAPI(DOC_ID, server=SERVER)


def get_directory_as_df():
    """
    Fetch back direcory of SSPHUB as a Panda dataframe

    Args:
        None

    Returns:
        A pl.DataFrame with three columns : ['email', 'Supprimez_mon_compte', 'nom', 'Nom_domaine']
    """
    # fetch all the rows
    api_directory = get_grist_directory_login()
    directory_df = api_directory.fetch_table('Contact')
    directory_df = pl.DataFrame(directory_df, infer_schema_length=None)

    # Selecting minimum set of columns
    cols_to_keep = [
        'email', 'Supprimez_mon_compte', 'nom', 'Nom_domaine'
        ]
    directory_df = directory_df.select(cols_to_keep)

    return directory_df


def get_emails():
    """
    Extract all emails that have not asked to be deteled from directory

    Returns:
        a single string with joined emails separated by ;

    Example:
        >>> get_emails()
        '<myemail@example.com>; <myemail2@example.com>'
    """
    my_directory_df = get_directory_as_df()
    my_directory_df = (my_directory_df.filter(pl.col('Supprimez_mon_compte') == False)
                                      .sort(['Nom_domaine', 'nom'])
                                      )
    # Turning emails from myemail@example.com to <myemail@example.com>
    my_directory_df.with_columns('<' + pl.col('email') + '>')
    # Joining all emails into one string '<myemail@example.com>; <myemail2@example.com>'
    return '; '.join(my_directory_df['email'])


def extract_emails_from_txt(file_path='ssphub_directory/input/replies.txt'):
    """
    Extract all email addresses from a file that contains all the automatic replies to a newsletter / an email.

    Args:
        file_path (str): The path to the file containing email addresses.

    Returns:
        list: A list of extracted email addresses.
    """
    # Regular expression pattern for matching email addresses
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    # Read the content of the file
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Find all email addresses in the content
    emails = re.findall(email_pattern, content)

    # Remove duplicate - Convert the list of email addresses to a set and back to list
    emails = set(emails)
    emails = list(emails)

    return emails


def export_list_to_csv(data_list, file_path):
    """
    Export a list to a CSV file using the csv module.

    Args:
        data_list (list): The list to export.
        file_path (str): The path to the CSV file.

    Returns:
        None

    """

    # Create the directory if it does not exist
    os.makedirs(file_path)

    # Writing the CSV
    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for item in data_list:
            writer.writerow([item])


#     UNUSED FOR NOW - A FIRST BRICK TO BUILD ON A FUNCTION TO AUTOMATICALLY DELETE ROWS BASED ON IDs
# def get_ids_of_email(emails_list):
#     """
#     Return the ids of the rows of the email in the GRIST directory

#     Args:
#         emails_list (list) : a list of strings, containing the emails to look for in df

#     Returns:
#         list: A list of ids of the rows in df

#     """
#     # Get the latest GRIST directory
#     api_directory = get_grist_directory_login()
#     directory_df = api_directory.fetch_table('Contact')
#     directory_df = pd.DataFrame(directory_df)

#     # Emails to dataframe
#     emails_df = pd.DataFrame({'emails':emails_list})

#     # Filter the emails
#     res = directory_df[directory_df['email'].isin(emails_df['emails'])]
#     res = res['id'].values.tolist()

#     return res


def fill_template(path_to_template, df, directory_output='ssphub_directory'):
    """
    Update the variables in a template QMD file with the ones from a data table.

    Args:
        df (pandas object): data frame where to have the values. A column must be named 'nom_dossier'
        qmd_file (str): The path to the template QMD file. Format 'my_folder/subfolder/template.qmd'
        directory_output (str): A string to paste before nom_dossier. Default is ssphub_directory/nom_dossier/index.qmd'
        !!! Don't put / at the end . For example : test is OK but test/ NOT OK
    """
    with open(path_to_template, 'r') as file:
        template_content = file.read()

    # Add directory before the output folder in df
    df['nom_dossier'] = directory_output.strip('/') + '/' + df['nom_dossier'].str.strip('/')

    for index, row in df.iterrows():
        for column in df.columns:
            variable_name = column
            variable_value = row[column]
            template_content = template_content.replace('{{' + variable_name + '}}', str(variable_value))

        # Create the output directory if it doesn't exist
        os.makedirs(row['nom_dossier'], exist_ok=True)

        output_file_path = row['nom_dossier'] + '/index.qmd'
        # If the file exists, we remove it
        if os.path.exists(output_file_path) and os.path.isfile(output_file_path):
            os.remove(output_file_path)

        with open(output_file_path, 'w') as res_file:
            res_file.write(template_content)
        
        print(f'File written at {output_file_path}')

    return template_content


def get_grist_merge_website_login():
    # Log in to GRIST API
    SERVER = "https://grist.numerique.gouv.fr/"
    DOC_ID = os.environ['SSPHUB_WEBSITE_MERGE_ID']

    if 'GRIST_API_KEY' not in os.environ:
        raise ValueError("The GRIST_API_KEY environment variable does not exist.")

    # Returning API details connection
    return GristDocAPI(DOC_ID, server=SERVER)


def get_grist_merge_as_df():
    """
    Get the table from GRIST to fetch all infos about index pages to create

    Arg:
        None

    Returns:
        A pl dataframe with columns matching the template variable names

    Example:
        >>> get_grist_merge_as_df()
        >>> get_grist_merge_as_df()
    id  ...                                     my_table_title
    0    2  ...  Travaux méthodologiques sur l'enquête Budget d...
    [17 rows x 12 columns]
    """
    # fetch all the rows
    api_merge = get_grist_merge_website_login()
    new_website_df = api_merge.fetch_table('Intranet_details')  
    # Pb with attachment column with polars, so pass by pandas
    new_website_df = pd.DataFrame(new_website_df)

    # Selecting useful columns
    cols_to_keep = ['id', 'Acteurs', 'Resultats', 'Details_du_projet',
       'sous_titre', 'Code_du_projet', 'tags', 'nom_dossier', 'date',
       'image', 'Titre', 'image']
    new_website_df = new_website_df[cols_to_keep]
    new_website_df['Titre_Tab'] = new_website_df['Titre']

    # Dictionnary for renaming variables / Right part must correspond to template keywords
    variable_mapping = {
        'Titre': 'my_title',
        'sous_titre': 'my_description',
        # 'auteurs': 'my_authors',
        'date': 'my_date',
        'image': 'my_image_path',
        'tags': 'my_categories',
        'Details_du_projet': 'my_table_details',
        'Acteurs': 'my_table_actors',
        'Resultats': 'my_table_results',
        'Code_du_projet': 'my_table_repo_path',
        'Titre_Tab': 'my_table_title'
    }

    new_website_df = new_website_df.rename(columns=variable_mapping)

    return new_website_df


def fill_all_templates_from_grist(path_to_template='ssphub_directory/template.qmd', directory='ssphub_directory'):
    """
    Wrapper of fill_template to automate creation of pages from the grist table

    Arg:
        path_to_template (string): the path of the template to use
        directory (string): the root directory where to save the files

    Returns:
        None

    Example:
        >>> fill_template('ssphub_directory/template.qmd', get_grist_merge_as_df(), 'ssphub_directory')
    """
    
    df = get_grist_merge_as_df()

    fill_template(path_to_template, df, directory_output=directory)

def get_grist_attachments_config():
    url = f'https://grist.numerique.gouv.fr/api/docs/{os.environ['SSPHUB_WEBSITE_MERGE_ID']}/attachments/archive'
    headers = {
        'Authorization': f'Bearer {os.environ['GRIST_API_KEY']}'
    }

    return url, headers

if __name__ == '__main__':
    path = '.temp/'
    if os.path.exists(path):
        shutil.rmtree(path)

    path = 'ssphub_directory/test/'
    if os.path.exists(path):
        shutil.rmtree(path)

    fill_all_templates_from_grist()
    generate_email(19, 'main', 'Infolettre de rentrée', get_emails())

