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
import os  # to remove temporary files
from grist_api import GristDocAPI  # To get directory emails
import pandas as pd  # to manage directory emails
import csv  # to store results of data cleaning
import re  # For pattern matching to search for emails


def generate_eml_file(email_body, recipient, subject, sender_email=":DG75-SSPHUB-Contact <SSPHUB-contact@insee.fr>"):
    # Create a multipart message
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['BCC'] = recipient
    msg['To'] = sender_email   # Auto send the email
    msg['From'] = 'SELECT THE RIGHT EMAIL'  # Set the sender's email address
    msg['X-Unsent'] = '1'  # Mark the email as unsent : when he file is opened, it can be sent.

    # Attach the HTML body
    msg.attach(MIMEText(email_body, 'html'))

    # Save the email as an .eml file
    eml_file_path = '.temp/email.eml'
    with open(eml_file_path, 'wb') as f:
        f.write(msg.as_bytes())

    print(f"Email saved as {eml_file_path}")


def fetch_qmd_file(url):
    # get the qmf file from an url and return it as string
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the .qmd file: {e}")
        return None


def process_qmd_file(qmd_content, qmd_output_file, newsletter_url='https://ssphub.netlify.app/infolettre/'):
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
    knitted to html

    Arg :
    - yaml_header: input yaml_header to clean, as string
    - newsletter_url: url of the newsletter to insert a link to that newsletter

    Returns:
    - url to raw Qmd newsletter
    - Output format : a string, with Unicode formating

    Example:

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
    - number: number of the newsletter
    - branch: branch of the repo to look for

    Returns:
    - Url to raw Qmd newsletter
    - Output format: a string
    """
    return f"https://raw.githubusercontent.com/InseeFrLab/ssphub/refs/heads/{branch}/infolettre/infolettre_{number}/index.qmd"


def published_url_newsletter(number):
    """
    Function to generate url of published newsletter on SSPHub website

    Arg :
    - number: number of the newsletter

    Returns:
    - url to ssphub website of the given newsletter
    - Output format: a string

    Example:
    published_url_newsletter('19')
    'https://ssphub.netlify.app/infolettre/infolettre_19/'
    """
    return f"https://ssphub.netlify.app/infolettre/infolettre_{number}/"


def list_raw_image_files(repo_owner, repo_name, subfolder_path, branch='main'):
    """
    List image files present in a given github folder. Images are defined by the following formats
    ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp')

    Arg :
    - repo_owner : name of the owner of the repo in Github
    - repo_name : name of the Github repo
    - subfolder_path : in the given repo architecture, a subfolder path to the folder where you want to list all files.
    For example : infolettre/infolettre_19/
    - branch where the newsletter is (main by default)

    Returns:
    - url to the raw images files
    - Output format: a list of strings

    Example:
    list_raw_image_files('InseeFrLab', 'ssphub', 'infolettre/infolettre_19', branch='main')
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
    - number of the newsletter
    - branch where the newsletter is (main by default)

    Returns:
    - list of path to the raw images files

    Example:
    list_image_files_for_newsletter('19', branch='main')
    ['https://raw.githubusercontent.com/InseeFrLab/ssphub/refs/heads/main/infolettre/infolettre_19/2025_09_back_school.png',
    'https://raw.githubusercontent.com/InseeFrLab/ssphub/refs/heads/main/infolettre/infolettre_19/measles-cases-historical-us-states-heatmap.png']

    """
    repo_owner = 'InseeFrLab'
    repo_name = 'ssphub'
    subfolder_path = f'infolettre/infolettre_{number}'

    return list_raw_image_files(repo_owner, repo_name, subfolder_path, branch)


def download_file(file_url, output_dir='.temp'):
    """
    Downloads a file from given url and store it in output_dir

    Arg:
    - file_url: url of the file to download, as a string
    - output_dir: directory where to save the file to, as a string

    Returns:
    - nothing
    - print if download was successfull

    Example:
    download_file('https://raw.githubusercontent.com/InseeFrLab/ssphub/refs/heads/main/infolettre/infolettre_19/2025_09_back_school.png')
    Image file downloaded to .temp/2025_09_back_school.png
    """

    try:
        # Send a GET request to the GitHub API
        response = requests.get(file_url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Extract the file name from the file path
        file_name = os.path.basename(file_url)

        # Save the file to the output directory
        output_path = os.path.join(output_dir, file_name)
        with open(output_path, 'wb') as f:
            f.write(response.content)

        print(f"Image file downloaded to {output_path}")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading image file: {e}")


def download_images_for_newsletter(number, branch='main', output_dir='.temp'):
    """
    Download all image files from given newsletter number and branch and store it in output_dir

    Arg:
    - number: number of the newsletter whose images will be downloaded, as a string
    - branch: repo branch of the newsletter (main for published newsletter, other for non published newsletters)
    - output_dir: directory where to save the files to, as a string

    Returns:
    - nothing
    - nb : a message is printed if download was successfull

    Example:
    download_file('https://raw.githubusercontent.com/InseeFrLab/ssphub/refs/heads/main/infolettre/infolettre_19/2025_09_back_school.png')
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
    - number (string): number of the newsletter to turn into email
    - branch (string): repo branch of the newsletter to turn into email (main for published newsletter, other for non published newsletters)
    - email_object (string): object of the email
    - email_dest (string) : list of email adresses to send the email to.
    - drop_temp (boolean): if temporary knitted files should be removed after knitting. Default is true

    Returns:
    - nothing

    Example:
    download_file('https://raw.githubusercontent.com/InseeFrLab/ssphub/refs/heads/main/infolettre/infolettre_19/2025_09_back_school.png')
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
        generate_eml_file(f.read(), email_dest, email_object)

    if drop_temp:
        os.remove(temp_file_qmd)
        os.remove(temp_file_html)


def get_api_login():
    # Log in to GRIST API
    SERVER = "https://grist.numerique.gouv.fr/"
    DOC_ID = os.environ['SSPHUB_DIRECTORY_ID']
    os.environ['GRIST_API_KEY'] = os.environ['MY_GRIST_API_KEY']

    # Returning API details connection
    return GristDocAPI(DOC_ID, server=SERVER)


def get_directory_as_df():
    # fetch all the rows
    api_directory = get_api_login()
    directory_df = api_directory.fetch_table('Contact')
    directory_df = pd.DataFrame(directory_df)

    # Selecting minimum set of columns and recreating domain name
    cols_to_keep = [
        'email', 'Supprimez_mon_compte', 'nom'
        ]
    directory_df = (directory_df.loc[:, cols_to_keep]
                                .assign(Nom_domaine=lambda df: df.email.str.split('@').str[1])
                   )

    return directory_df


def get_emails():
    """
    Extract all emails that have not asked to be deteled from directory

    Returns:
        a single string with joined emails : '<email1@com.com>;<email2@fr.fr>'
    """
    my_directory_df = get_directory_as_df()
    my_directory_df = (my_directory_df.query('Supprimez_mon_compte == False')
                                      .sort_values(['Nom_domaine', 'nom'])
                                      )
    # Turning emails from myemail@example.com to <myemail@example.com>
    my_directory_df['email'] = '<' + my_directory_df['email'] + '>'
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
#     api_directory = get_api_login()
#     directory_df = api_directory.fetch_table('Contact')
#     directory_df = pd.DataFrame(directory_df)

#     # Emails to dataframe
#     emails_df = pd.DataFrame({'emails':emails_list})

#     # Filter the emails
#     res = directory_df[directory_df['email'].isin(emails_df['emails'])]
#     res = res['id'].values.tolist()

#     return res


def fill_template(path_to_template, df, path_to_output='ssphub_directory/'):
    """
    Update the variables in a template QMD file with the ones from a data table.

    Args:
        df (Panda object): data frame where to have the values. A column must be named 'nom_dossier'
        qmd_file (str): The path to the template QMD file. Format 'my_folder/subfolder/template.qmd'
        path_to_output (str): A string to paste before nom_dossier. Default is ssphub_directory/nom_dossier/index.qmd'
    """
    with open(path_to_template, 'r') as file:
        template_content = file.read()

    # Add path to output before the one in df
    df['nom_dossier'] = path_to_output + '/' + df['nom_dossier'].str.strip('/')

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

    return template_content


def get_api_website_login():
    # Log in to GRIST API
    SERVER = "https://grist.numerique.gouv.fr/"
    DOC_ID = os.environ['SSPHUB_WEBSITE_MERGE_ID']
    os.environ['GRIST_API_KEY'] = os.environ['MY_GRIST_API_KEY']

    # Returning API details connection
    return GristDocAPI(DOC_ID, server=SERVER)


def get_website_merge_as_df():
    """
    Get the table from GRIST to fetch all infos about index pages to create

    Arg:
        None

    Returns:
        A pd dataframe with columns matching the template variable names
    """
    # fetch all the rows
    api_merge = get_api_website_login()
    new_website_df = api_merge.fetch_table('Intranet_details')
    new_website_df = pd.DataFrame(new_website_df)

    # Selecting useful columns
    cols_to_keep = ['id', 'Acteurs', 'Resultats', 'Details_du_projet',
       'sous_titre', 'Code_du_projet', 'tags', 'nom_dossier', 'date',
       'image', 'Titre']
    new_website_df = new_website_df[cols_to_keep]

    new_website_df['Titre_Tab'] = new_website_df['Titre']

    # Dictionnary for renaming variables / Right part must correspond to template keywords
    variable_mapping = {
        'Titre': 'my_title',
        'sous_titre': 'my_description',
        'auteurs': 'my_authors',
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
