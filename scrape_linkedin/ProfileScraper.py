from .Scraper import Scraper
from .ConnectionScraper import ConnectionScraper
import json
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException

import time
from .Profile import Profile
from .utils import AnyEC

class ProfileScraper(Scraper):
    """
    Scraper for Personal LinkedIn Profiles. See inherited Scraper class for
    details about the constructor.
    """
    MAIN_SELECTOR = '.core-rail'
    ERROR_SELECTOR = '.profile-unavailable'

    def scrape_by_email(self, email):
        self.load_profile_page(
            'https://www.linkedin.com/sales/gmail/profile/proxy/{}'.format(email))
        return self.get_profile()

    def scrape(self, url='', user=None):
        print("Scrape:",user)
        self.load_profile_page(url, user)
        content = self.get_profile()
        return content

    def load_profile_page(self, url='', user=None):
        """Load profile page and all async content

        Params:
            - url {str}: url of the profile to be loaded
        Raises:
            ValueError: If link doesn't match a typical profile url
        """
        if user:
            url = 'http://www.linkedin.com/in/' + user
        if 'com/in/' not in url and 'sales/gmail/profile/proxy/' not in url:
            raise ValueError(
                "Url must look like... .com/in/NAME or... '.com/sales/gmail/profile/proxy/EMAIL")
        self.driver.get(url)
        # Wait for page to load dynamically via javascript
        try:
            myElem = WebDriverWait(self.driver, self.timeout).until(AnyEC(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self.MAIN_SELECTOR)),
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self.ERROR_SELECTOR))
            ))
        except TimeoutException as e:
            raise ValueError(
                """Took too long to load profile.  Common problems/solutions:
                1. Invalid LI_AT value: ensure that yours is correct (they
                   update frequently)
                2. Slow Internet: increase the time out parameter in the Scraper
                   constructor
                3. Invalid e-mail address (or user does not allow e-mail scrapes) on scrape_by_email call
                """)

        # Check if we got the 'profile unavailable' page
        try:
            self.driver.find_element_by_css_selector(self.MAIN_SELECTOR)
        except:
            raise ValueError(
                'Profile Unavailable: Profile link does not match any current Linkedin Profiles')
        # Scroll to the bottom of the page incrementally to load any lazy-loaded content
        self.scroll_to_bottom()
        self.expand_given_recommendations()

    def expand_given_recommendations(self):
        try:
            given_recommendation_tab = self.driver.find_element_by_css_selector(
                'section.pv-recommendations-section button[aria-selected="false"].artdeco-tab')
            # Scrolls the desired element into view
            self.driver.execute_script(
                "arguments[0].scrollIntoView(false);", given_recommendation_tab)
            given_recommendation_tab.click()
            self.click_expandable_buttons()
            # self.scroll_to_bottom()
        except:
            pass

    def get_profile(self):
        try:
            profile = self.driver.find_element_by_css_selector(
                self.MAIN_SELECTOR).get_attribute("outerHTML")
        except:
            raise Exception(
                "Could not find profile wrapper html. This sometimes happens for exceptionally long profiles.  Try decreasing scroll-increment.")
        interest_details = self.get_interests_info()
        
        button = self.driver.find_element_by_css_selector(
                '.pv-interests-modal button')
        button.click()
        contact_info = self.get_contact_info()
        return Profile(profile + contact_info + interest_details)

    def get_contact_info(self):
        try:
            # Scroll to top to put clickable button in view
            self.driver.execute_script("window.scrollTo(0, 0);")
            button = self.driver.find_element_by_css_selector(
                'a[data-control-name="contact_see_more"]')
            button.click()
            contact_info = self.wait_for_el('.pv-contact-info')
            return contact_info.get_attribute('outerHTML')
        except Exception as e:
            print(e)
            return ""
    
    def checkTabLoad(self, selector, oldContent):
        content = self.driver.find_element_by_css_selector(selector)
        if oldContent == content:
            return True
        else:
            return False
        
    def get_interests_info(self):
        content = ""
        try:
            try:
                button = self.driver.find_element_by_css_selector(
                    'a[data-control-name="view_interest_details"]')
                button.click()
                time.sleep(2)
                #Get Influencer Details
                influencer_details = self.wait_for_el('.pv-interests-list .entity-list-wrapper')
                self.driver.execute_script("arguments[0].scrollIntoView(true);", influencer_details);
                time.sleep(1)
                self.driver.execute_script("arguments[0].scrollIntoView(true);", influencer_details);
                time.sleep(1)
                content = influencer_details.get_attribute('outerHTML') 
                content = content.replace('entity-list-wrapper','influencer_details')
            except:
                # Continue running script
                print("No Influencer associated")
            
            try:
                #Get companies details
                button = self.driver.find_element_by_css_selector(
                    'a[data-control-name="following_companies"]')
                button.click()
                self.driver.implicitly_wait(2)
                self.wait(EC.staleness_of(self.driver.find_element_by_css_selector('.pv-interests-list .entity-list-wrapper')))
                companies = self.wait_for_el('.pv-interests-list .entity-list-wrapper')
                time.sleep(2)
                self.driver.execute_script("arguments[0].scrollIntoView(true);", companies);
                time.sleep(1)
                content += companies.get_attribute('outerHTML').replace('entity-list-wrapper','following_companies')
            except:
                # Continue running script
                print("No Companies associated")
            
            try:
                #Get Groups data
                button = self.driver.find_element_by_css_selector(
                    'a[data-control-name="following_groups"]')
                button.click()
                self.wait(EC.staleness_of(self.driver.find_element_by_css_selector('.pv-interests-list .entity-list-wrapper')))
                groups = self.wait_for_el('.pv-interests-list .entity-list-wrapper')
                content += groups.get_attribute('outerHTML').replace('entity-list-wrapper','following_groups')
            except:
                # Continue running script
                print("No Groups associated")
                
            try:
                #Get Schools
                button = self.driver.find_element_by_css_selector(
                    'a[data-control-name="following_schools"]')
                button.click()
                self.wait(EC.staleness_of(self.driver.find_element_by_css_selector('.pv-interests-list .entity-list-wrapper')))
                schools = self.wait_for_el('.pv-interests-list .entity-list-wrapper')
                content += schools.get_attribute('outerHTML').replace('entity-list-wrapper','following_schools')
            except:
                # Continue running script
                print("No Schools associated")
            
            return content
        except Exception as e:
            print(e)
            return ""

    def get_mutual_connections(self):
        try:
            link = self.driver.find_element_by_partial_link_text(
                'Mutual Connection')
        except NoSuchElementException as e:
            print("NO MUTUAL CONNS")
            return []
        with ConnectionScraper(scraperInstance=self) as cs:
            cs.driver.get(link.get_attribute('href'))
            cs.wait_for_el('.search-s-facet--facetNetwork form button')
            return cs.scrape_all_pages()
