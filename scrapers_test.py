import json
import os
import scrape_linkedin
from scrape_linkedin import ProfileScraper #, scrape_in_parallel
import importlib

importlib.reload(scrape_linkedin)

class LinkedInScraper:
    """
    docstring
    """

    @staticmethod
    def scrapper(actual_name, linkedin_username,linkedInCreds):
        #user_data = None
        print("Running Linked In scrapper for ", actual_name)
        
        json_file_name = linkedin_username.lower()
        json_file_name = json_file_name.replace(" ", "_")
        json_file_name = f"{json_file_name}_linkedin.json"
        '''
        scrape_in_parallel(
            scraper_type=ProfileScraper,
            items=[linkedin_username],
            output_file="Output\\LinkedIn\\"+json_file_name,
            num_instances=1
        )
        '''

        #credentials = {"email":linkedInCreds["linkedInEmail"], "password":linkedInCreds["linkedInPassword"]}
        scraper = ProfileScraper(credentials=linkedInCreds, scroll_pause=.1)
        user_data = scraper.scrape(user=linkedin_username)
        result = {}
        for key, value in user_data.items():
            result[key] = value.to_dict()
        # Fix the value of followers
        result['profile']["personal_info"]["followers"] = result['profile']["personal_info"]["followers"][9:result['profile']["personal_info"]["followers"].index("followers")].strip()
        
        with open(json_file_name, 'w') as outfile:
            json.dump(result, outfile)

        return json_file_name


credentials = {"email":"uditsrn28@gmail.com", "password":"Nc1hr@@r8u7d12804199190"}
LinkedInScraper.scrapper('Udit Sarin', 'uditsarin',credentials)
