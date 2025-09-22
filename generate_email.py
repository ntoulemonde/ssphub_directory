# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "email-mime",
#     "pyyaml",
#     "requests",
# ]
# ///

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests  # To transform newsletter into email
import yaml  # To transform newsletter into email
import os 

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
    eml_file_path = 'email.eml'
    with open(eml_file_path, 'wb') as f:
        f.write(msg.as_bytes())

    print(f"Email saved as {eml_file_path}")


# To get the qmf file from an url and return it as string
def fetch_qmd_file(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the .qmd file: {e}")
        return None


def process_qmd_file(qmd_content, qmd_output_file, newsletter_url = 'https://ssphub.netlify.app/infolettre/'):
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
    cleaned_yaml['format'] = {'html': {'self-contained': True}}

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


def get_raw_url_newsletter(number, branch='main'):
    # number = 19
    # branch = 'newsletter_v3'
    
    qmd_url = ('https://raw.githubusercontent.com/InseeFrLab/ssphub/refs/heads/'+ 
        str(branch) + 
        '/infolettre/infolettre_' + 
        str(number) + '/index.qmd'
        )
    
    return qmd_url


def get_published_url_newsletter(number):
    # number = 19
    
    newsletter_url = ('https://ssphub.netlify.app/infolettre/infolettre_' + 
        str(number)  + 
        '/'
        )
    
    return newsletter_url


def generate_email(number, branch, email_object, email_dest, drop_temp=True):
    # Test
    number = 19

    temp_file='./temp'
    temp_file_qmd = temp_file + '.qmd'
    temp_file_html = temp_file + '.html'


    qmd_content = fetch_qmd_file(get_raw_url_newsletter(number, branch))
    process_qmd_file(qmd_content, temp_file_qmd, get_published_url_newsletter(number))
    knit_to_html(temp_file_qmd)

    with open(temp_file_html, 'r', encoding="utf-8") as f:
        generate_eml_file(f.read(), email_dest, email_object)

    if drop_temp:
        os.remove(temp_file_qmd)
        os.remove(temp_file_html)


generate_email(19, 'newsletter_v3', 'Test', 'example@hi.fr')
 
