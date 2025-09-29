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
import csv  # To export results as csv

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
    cleaned_yaml_str = yaml.dump(cleaned_yaml, sort_keys=False,  allow_unicode= True, width=4096)
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
    return f"https://raw.githubusercontent.com/InseeFrLab/ssphub/refs/heads/{branch}/infolettre/infolettre_{number}/index.qmd"


def published_url_newsletter(number):
    return f"https://ssphub.netlify.app/infolettre/infolettre_{number}/"


def list_image_files_in_subfolder(repo_owner, repo_name, subfolder_path, branch='main'):
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
            item['path'] for item in contents
            if item['type'] == 'file' and os.path.splitext(item['name'])[1].lower() in image_extensions
        ]

        return image_files
    except requests.exceptions.RequestException as e:
        print(f"Error fetching contents from GitHub API: {e}")
        return None


def get_image_files_for_newsletter(number, branch='main'):
    repo_owner = 'InseeFrLab'
    repo_name = 'ssphub'
    subfolder_path = f'infolettre/infolettre_{number}'

    return list_image_files_in_subfolder(repo_owner, repo_name, subfolder_path, branch)


def download_image_file(repo_owner, repo_name, file_path, branch='main', output_dir='.temp'):
    # GitHub API URL to fetch the raw content of the file
    url = f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/{branch}/{file_path}"

    try:
        # Send a GET request to the GitHub API
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Extract the file name from the file path
        file_name = os.path.basename(file_path)

        # Save the file to the output directory
        output_path = os.path.join(output_dir, file_name)
        with open(output_path, 'wb') as f:
            f.write(response.content)

        print(f"Image file downloaded to {output_path}")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading image file: {e}")


def download_image_files_for_newsletter(number, branch='main', output_dir='.temp'):
    repo_owner = 'InseeFrLab'
    repo_name = 'ssphub'

    # Get the list of image files in the subfolder
    image_files = get_image_files_for_newsletter(number, branch)

    if not image_files:
        print("No image files found in the subfolder.")

    # Download each image file
    downloaded_files = []
    for image_file in image_files:
        downloaded_file = download_image_file(repo_owner, repo_name, image_file, branch, output_dir)
        if downloaded_file:
            downloaded_files.append(downloaded_file)

    return downloaded_files


def generate_email(number, branch, email_object, email_dest, drop_temp=True):
    temp_file = './.temp/temp'
    temp_file_qmd = temp_file + '.qmd'
    temp_file_html = temp_file + '.html'

    download_image_files_for_newsletter(number, branch, '.temp')

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
    print(directory_df.groupby('Supprimez_mon_compte')['id'].nunique())

    # renaming weird column
    directory_df = directory_df.rename(columns={'gristHelper_Display': 'nom_structure'})

    # Selecting useful columns
    cols_to_keep = [
        'id', 'nom', 'prenom', 'email', 'Structure', 'Ajout_date', 'Supprimez_mon_compte',
        'Nom_domaine', 'Siren_structure', 'nom_structure',
    ]
    directory_df = directory_df[cols_to_keep]

    return directory_df



def get_emails():
    # Extract all emails that have not asked to be deteled from directory
    my_directory_df = get_directory_as_df()
    my_directory_df = (my_directory_df.query('Supprimez_mon_compte == False')
                                      .sort_values(['Nom_domaine', 'nom'])
                                      )
    # Turning emails from myemail@example.com to <myemail@example.com>
    my_directory_df['email'] = '<' + my_directory_df['email'] + '>'
    return '; '.join(my_directory_df['email'])


# Test
# generate_email(19, 'newsletter_v3', 'Infolettre de rentrée', 'test', True)
# generate_email(17, 'main', 'Infolettre de rentrée', get_emails())



def extract_emails(file_path='ssphub_directory/input/replies.txt'):
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
    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for item in data_list:
            writer.writerow([item])


# export_list_to_csv(extract_emails(), 'output/temp.csv')


def get_api_login():
    # Log in to GRIST API
    SERVER = "https://grist.numerique.gouv.fr/"
    DOC_ID = os.environ['SSPHUB_DIRECTORY_ID']
    os.environ['GRIST_API_KEY'] = os.environ['MY_GRIST_API_KEY']

    # Returning API details connection
    return GristDocAPI(DOC_ID, server=SERVER)


def get_ids_of_email(emails_list):
    """
    Return the ids of the rows of the email in the GRIST directory

    Args:
        emails_list (list) : a list of strings, containing the emails to look for in df

    Returns:
        list: A list of ids of the rows in df
    """
    # Get the latest GRIST directory 
    api_directory = get_api_login()
    directory_df = api_directory.fetch_table('Contact')
    directory_df = pd.DataFrame(directory_df)

    # Emails to dataframe
    emails_df = pd.DataFrame({'emails':emails_list})

    # Filter the emails
    res = directory_df[directory_df['email'].isin(emails_to_delete['emails'])]
    res = res['id'].values.tolist()
    
    return res

# get_ids_of_email(extract_emails())
