# Objective

Tools to manage [SSPHub's](https://ssphub.netlify.app/) directory and [SSPHub's](https://ssphub.netlify.app/) newsletter system. 

# Use

## Requirements
- Have access to GRIST directory
- Have : 
    - GRIST_API_KEY : your API Key to use Grist (see [GRIST documentation](https://support.getgrist.com/rest-api/) to see how to access it)
    - GRIST_SSPHUB_DIRECTORY_ID : GRIST id of the SSPHub's Directory document (available on Grist)
    - GRIST_SSPHUB_WEBSITE_MERGE_ID : GRIST id of the internal table to merge old website to new website (available on Grist)
- Apps : Python

## Step by step 

### Newsletter
L'objectif ici est de valider et d'envoyer la newsletter du SSPHub aux membres inscrits sur Grist.  
- Validation de la newsletter :
    - Faire une PR sur le site
    - Envoyer le lien à RL, MH
    - reprendre les commentaires
    - Ouvrir Onyxia
    - Avoir ce repo chargé
    - `cd <This repo>`  
    - Faire `uv sync` 
    - Set interpreter path : F1 in VS Code and then select interpreter and choose <this.repo>/.venv/bin/python
    - go to script to generate email for validation
    - download email
    - add text to say It's the newsletter for clearance
    - send it
- Envoi de la newsletter
    - To generate draft email, go to script.py, and run function generate_email with Object 
    - Download email
    - Check the newsletter (format, typos etc)
    - Select the right Outlook account
    - Press Send
- Après envoi : 
    - Cleaning de la mailing list : copier tous les messages d'erreurs dans un fichier "replies.txt"
    - Pour les supprimer : 
        - Manuel : Function add_to_grist_delete_table va en extraire les emails et les poster sur Grist
        - Automatique : Function delete_email_from_contact_table va extraire les emails et les supprimer de la table Contact de Grist

### Fusion site SSPHub / SSPLab
 - To import draft template to SSPHub's site, go to script.py and run fill_all_templates_from_grist
 
