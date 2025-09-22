# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "grist-api",
#     "pandas",
# ]
# ///

import os
from grist_api import GristDocAPI
import pandas as pd

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

    return directory_df[cols_to_keep]


def get_emails():
    # Extract all emails that have not asked to be deteled from directory
    my_directory_df = get_directory_as_df()
    my_directory_df = (my_directory_df.query('Supprimez_mon_compte == False')
                                      .sort_values(['Nom_domaine', 'nom'])
                                      )
    # Turning emails from myemail@example.com to <myemail@example.com>
    my_directory_df['email'] = '<' + my_directory_df['email'] + '>'                    
    return '; '.join(my_directory_df['email'])


get_emails()

