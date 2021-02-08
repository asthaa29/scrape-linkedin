from .utils import *
from .ResultsObject import ResultsObject
import re
from datetime import datetime


class Profile(ResultsObject):
    """Linkedin User Profile Object"""

    attributes = ['personal_info', 'experiences',
                  'skills', 'accomplishments', 'interests', 'recommendations',
                  'influencers','companies','groups','schools']

    @property
    def personal_info(self):
        """Return dict of personal info about the user"""
        top_card = one_or_default(self.soup, '.pv-top-card')
        contact_info = one_or_default(self.soup, '.pv-contact-info')

        # Note that some of these selectors may have multiple selections, but
        # get_info takes the first match
        personal_info = get_info(top_card, {
            'name': '.pv-top-card--list > li',
            'headline': '.flex-1.mr5 h2',
            'company': 'li a[data-control-name="position_see_more"]',
            'school': 'li a[data-control-name="education_see_more"]',
            'location': '.pv-top-card--list-bullet > li',
            'connected': '.pv-top-card--list-bullet > li:nth-child(2)'
        })

        personal_info['summary'] = text_or_default(
            self.soup, '.pv-about-section .pv-about__summary-text', '').replace('... see more', '').strip()

        image_url = ''
        # If this is not None, you were scraping your own profile.
        image_element = one_or_default(
            top_card, 'img.profile-photo-edit__preview')

        if not image_element:
            image_element = one_or_default(
                top_card, 'img.pv-top-card__photo')

        # Set image url to the src of the image html tag, if it exists
        try:
            image_url = image_element['src']
        except:
            pass

        personal_info['image'] = image_url

        followers_text = text_or_default(self.soup,
                                         '.pv-recent-activity-section-v2', '')
        followers_text = followers_text.strip()
        personal_info['followers'] = followers_text

        # print(contact_info)
        personal_info.update(get_info(contact_info, {
            'email': '.ci-email .pv-contact-info__ci-container',
            'phone': '.ci-phone .pv-contact-info__ci-container',
            #'connected': '.ci-connected .pv-contact-info__ci-container'
        }))

        personal_info['websites'] = []
        if contact_info:
            websites = contact_info.select('.ci-websites li a')
            websites = list(map(lambda x: x['href'], websites))
            personal_info['websites'] = websites

        return personal_info

    @property
    def experiences(self):
        """
        Returns:
            dict of person's professional experiences.  These include:
                - Jobs
                - Education
                - Certification and Licenses
                - Volunteer Experiences
        """
        experiences = {}
        container = one_or_default(self.soup, '.background-section')

        jobs = all_or_default(
            container, '#experience-section ul .pv-position-entity')
        jobs = list(map(get_job_info, jobs))
        jobs = flatten_list(jobs)

        experiences['jobs'] = jobs

        schools = all_or_default(
            container, '#education-section .pv-education-entity')
        schools = list(map(get_school_info, schools))
        experiences['education'] = schools
        
        cert_licenses = all_or_default(
            container, '#certifications-section .pv-certification-entity')
        cert_licenses = list(map(get_certification_info, cert_licenses))
        experiences['certifications'] = cert_licenses

        volunteering = all_or_default(
            container, '.pv-profile-section.volunteering-section .pv-volunteering-entity')
        volunteering = list(map(get_volunteer_info, volunteering))
        experiences['volunteering'] = volunteering

        return experiences

    @property
    def skills(self):
        """
        Returns:
            list of skills {name: str, endorsements: int} in decreasing order of
            endorsement quantity.
        """
        # Identify top skills
        
        skillsList = []
        
        container = one_or_default(self.soup, '.pv-skill-categories-section__top-skills')
        topSkills = all_or_default(container, '.pv-skill-category-entity__skill-wrapper')
        topSkills = list(map(get_skill_info, topSkills))
        
        skillsList.append({"category":"Top Skills", "skills": topSkills})
        
        skillLists = one_or_default(self.soup, ".pv-skill-categories-section")
        skillCategories = all_or_default(skillLists, '.pv-skill-category-list')
        for category in skillCategories:
            skillListHeading = text_or_default(category, '.pv-skill-categories-section__secondary-skill-heading')
            skills = all_or_default(category,'.pv-skill-category-entity__skill-wrapper')
            skills = list(map(get_skill_info, skills))
            skillsList.append({"category": skillListHeading, "skills": skills})
            
        return skillsList 

    @property
    def accomplishments(self):
        """
        Returns:
            dict of professional accomplishments including:
                - publications
                - patents
                - courses
                - projects
                - honors
                - test scores
                - languages
                - organizations
        """
        accomplishments = dict.fromkeys([
            'publications', 'patents',
            'courses', 'projects', 'honors',
            'test_scores', 'languages', 'organizations'
        ])
        container = one_or_default(self.soup, '.pv-accomplishments-section')
        for key in accomplishments:
            accs = all_or_default(container, 'section.' + key + ' ul > li')
            accs = map(lambda acc: acc.get_text() if acc else None, accs)
            accomplishments[key] = list(accs)
        return accomplishments

    @property
    def interests(self):
        """
        Returns:
            list of person's interests
        """
        container = one_or_default(self.soup, '.pv-interests-section')
        interests = all_or_default(container, 'ul > li')
        interests = map(lambda i: text_or_default(
            i, '.pv-entity__summary-title'), interests)
        
        return list(interests)
    
    @property
    def influencers(self):
        """
        Returns:
            list of person's interests
        """
        container = one_or_default(self.soup, '.influencer_details')
        influencers = all_or_default(container, 'ul > li')
        influencers = map(lambda i: text_or_default(
            i, '.pv-entity__summary-title-text'), influencers)
        
        return list(influencers)
    
    @property
    def companies(self):
        """
        Returns:
            list of person's interests
        """
        container = one_or_default(self.soup, '.following_companies')
        companies = all_or_default(container, 'ul > li')
        companies = map(lambda i: text_or_default(
            i, '.pv-entity__summary-title-text'), companies)

        return list(companies)
    
    @property
    def groups(self):
        """
        Returns:
            list of person's interests
        """
        container = one_or_default(self.soup, '.following_groups')
        groups = all_or_default(container, 'ul > li')
        
        groups = map(lambda i: text_or_default(
            i, '.pv-entity__summary-title-text'), groups)        
        
        return list(groups)
    
    @property
    def schools(self):
        """
        Returns:
            list of person's interests
        """
        container = one_or_default(self.soup, '.following_schools')
        schools = all_or_default(container, 'ul > li')
        schools = map(lambda i: text_or_default(
            i, '.pv-entity__summary-title-text'), schools)
        
        return list(schools)

    @property
    def recommendations(self):
        recs = {
            'received': [],
            'given': [],
        }
        rec_block = one_or_default(
            self.soup, 'section.pv-recommendations-section')
        received, given = all_or_default(rec_block, 'div.artdeco-tabpanel')
        for rec_received in all_or_default(received, "li.pv-recommendation-entity"):
            recs["received"].append(get_recommendation_details(rec_received))

        for rec_given in all_or_default(given, "li.pv-recommendation-entity"):
            recs["given"].append(get_recommendation_details(rec_given))

        return recs

    def to_dict(self):
        info = super(Profile, self).to_dict()
        info['personal_info']['current_company_link'] = ''
        jobs = info['experiences']['jobs']
        if jobs and jobs[0]['date_range'] and 'present' in jobs[0]['date_range'].lower():
            info['personal_info']['current_company_link'] = jobs[0]['li_company_url']
        else:
            print("Unable to determine current company...continuing")
        return info
