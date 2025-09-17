import os
from grist_api import GristDocAPI
import pandas as pd

# Log in to GRIST API
SERVER = "https://grist.numerique.gouv.fr/"
DOC_ID = os.environ['SSPHUB_DIRECTORY_ID']
os.environ['GRIST_API_KEY'] = os.environ['MY_GRIST_API_KEY']

# Defining API details connection
api_directory = GristDocAPI(DOC_ID, server=SERVER)

# fetch all the rows
directory_df = api_directory.fetch_table('Contact')
directory_df = pd.DataFrame(directory_df)
directory_df.groupby('Supprimez_mon_compte')['id'].nunique()

# renaming weird column
directory_df = directory_df.rename(columns={'gristHelper_Display': 'nom_structure'})

# Selecting useful columns
cols_to_keep = [
    'id', 'nom', 'prenom', 'email', 'Structure', 'Ajout_date', 'Supprimez_mon_compte',
    'Nom_domaine', 'Siren_structure', 'nom_structure',
]
directory_df = directory_df[cols_to_keep]

# Function to extract all emails that have not asked to be deteled from directory
def get_emails(my_directory_df):
    my_directory_df = (my_directory_df.query('Supprimez_mon_compte == False')
                                .sort_values(['Nom_domaine', 'nom'])
                      )
    return ', '.join(my_directory_df['email'])

get_emails(directory_df)