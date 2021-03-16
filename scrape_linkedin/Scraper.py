import selenium.webdriver
import time
from os import environ
from abc import abstractmethod
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from webdriver_manager.chrome import ChromeDriverManager

from .utils import *

class Scraper(object):
    """
    Wrapper for selenium Chrome driver with methods to scroll through a page and
    to scrape and parse info from a linkedin page

    Params:
        - cookie {str}: li_at session cookie required to scrape linkedin profiles
        - driver {webdriver}: driver to be used for scraping
        - scroll_pause {float}: amount of time to pause (s) while incrementally
        scrolling through the page
        - scroll_increment {int}: pixel increment for scrolling
        - timeout {float}: time to wait for page to load first batch of async content
    """

    def __init__(self, cookie=None, scraperInstance=None, driver=selenium.webdriver.Chrome, driver_options={}, scroll_pause=0.1, scroll_increment=300, timeout=10, credentials = None):
        if type(self) is Scraper:
            raise Exception(
                'Scraper is an abstract class and cannot be instantiated directly')

        if scraperInstance:
            self.was_passed_instance = True
            self.driver = scraperInstance.driver
            self.scroll_increment = scraperInstance.scroll_increment
            self.timeout = scraperInstance.timeout
            self.scroll_pause = scraperInstance.scroll_pause
            return

        self.was_passed_instance = False
        self.driver = driver(ChromeDriverManager().install(),**driver_options)
        self.scroll_pause = scroll_pause
        self.scroll_increment = scroll_increment
        self.timeout = timeout
        self.driver.get('http://www.linkedin.com')
        self.driver.set_window_size(1920, 1080)
        
        email = ""
        if credentials:
            email = credentials["email"]
            password = credentials["password"]
            
        if email:
            self.login(email, password)
        elif 'LI_EMAIL' in environ and 'LI_PASS' in environ:
            self.login(environ['LI_EMAIL'], environ['LI_PASS'])
        else:
            if not cookie and 'LI_AT' not in environ:
                raise ValueError(
                    'Must either define LI_AT environment variable, or pass a cookie string to the Scraper')
            elif not cookie:
                cookie = environ['LI_AT']
            self.driver.add_cookie({
                'name': 'li_at',
                'value': cookie,
                'domain': '.linkedin.com'
            })

    @abstractmethod
    def scrape(self):
        raise Exception('Must override abstract method scrape')

    def login(self, email, password):
        email_input = self.driver.find_element_by_id("session_key")
        email_input.send_keys(email)

        password_input = self.driver.find_element_by_id("session_password")
        password_input.send_keys(password)
        
        password_input.send_keys(Keys.ENTER)

    def get_html(self, url):
        self.load_profile_page(url)
        return self.driver.page_source

    def scroll_to_bottom(self):
        """Scroll to the bottom of the page

        Params:
            - scroll_pause_time {float}: time to wait (s) between page scroll increments
            - scroll_increment {int}: increment size of page scrolls (pixels)
        """
        # NOTE: this starts scrolling from the current scroll position, not the top of the page.
        current_height = self.driver.execute_script(
            "return document.documentElement.scrollTop")
        while True:
            self.click_expandable_buttons()
            # Scroll down to bottom in increments of self.scroll_increment
            new_height = self.driver.execute_script(
                "return Math.min({}, document.body.scrollHeight)".format(current_height + self.scroll_increment))
            if (new_height == current_height):
                break
            self.driver.execute_script(
                "window.scrollTo(0, {});".format(new_height))
            current_height = new_height
            # Wait to load page
            time.sleep(self.scroll_pause)

    def click_expandable_buttons(self):
        expandable_button_selectors = [
            'button[aria-expanded="false"].pv-skills-section__additional-skills',
            'button[aria-expanded="false"].pv-profile-section__see-more-inline',
            'button[aria-expanded="false"].pv-top-card-section__summary-toggle-button',
            'button[aria-expanded="false"].inline-show-more-text__button',
            'button[data-control-name="contact_see_more"]'
        ]
        for name in expandable_button_selectors:
            try:
                self.driver.find_element_by_css_selector(name).click()
            except:
                pass
         # Use JQuery to click on invisible expandable 'see more...' elements
        self.driver.execute_script(
            'document.querySelectorAll(".lt-line-clamp__ellipsis:not(.lt-line-clamp__ellipsis--dummy) .lt-line-clamp__more").forEach(el => el.click())')

    def scroll_to_bottom_activity(self):
        """Scroll to the bottom of the page

        Params:
            - scroll_pause_time {float}: time to wait (s) between page scroll increments
            - scroll_increment {int}: increment size of page scrolls (pixels)
        """
        # NOTE: this starts scrolling from the current scroll position, not the top of the page.
        current_height = self.driver.execute_script(
            "return document.documentElement.scrollTop")
        while True:
            self.click_expandable_buttons()
            # Scroll down to bottom in increments of self.scroll_increment
            new_height = self.driver.execute_script(
                "return Math.min({}, document.body.scrollHeight)".format(current_height + self.scroll_increment))
            value_found = self.driver.find_elements_by_class_name('feed-shared-actor__sub-description')[-1].find_element_by_tag_name('span').find_element_by_tag_name('span').text
            print(value_found[:3])
            if new_height == current_height or value_found[:3] == '2mo':
                break
            self.driver.execute_script(
                "window.scrollTo(0, {});".format(new_height))
            current_height = new_height
            # Wait to load page
            time.sleep(self.scroll_pause)


    def wait(self, condition):
        return WebDriverWait(self.driver, self.timeout).until(condition)

    def wait_for_el(self, selector):
        return self.wait(EC.presence_of_element_located((
            By.CSS_SELECTOR, selector
        )))

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.quit()

    def quit(self):
        if self.driver and not self.was_passed_instance:
            self.driver.quit()
    
    # Deleting (Calling destructor) 
    def __del__(self): 
        self.quit()
