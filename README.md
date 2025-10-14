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

 - To generate draft email, go to script.py, and run function generate_email
 - To import draft template to SSPHub's site, go to script.py and run fill_all_templates_from_grist
 
