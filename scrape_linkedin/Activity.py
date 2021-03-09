from .utils import *
from .ResultsObject import ResultsObject
import re
from datetime import datetime


class Activity(ResultsObject):
    """Linkedin User Profile Object"""

    attributes = ['activities']

    @property
    def activities(self):
        """Return dict of personal info about the user"""
        top_card = all_or_default(self.soup, '.occludable-update')
        information = []
        for i in top_card:
            action = text_or_default(i,'.t-12')
            if action is not None and not any(a in action for a in ['likes', 'liked', 'replied', 'commented']):
                element = {}
                element['post'] = text_or_default(i,'.feed-shared-update-v2__description-wrapper')
                element['no_of_likes'] = text_or_default(i, '.social-details-social-counts__count-value')
                element['no_of_comments'] = text_or_default(i, '.social-details-social-counts__comments')
                information.append(element)

        return information

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

    def to_dict(self):
        info = super(Activity, self).to_dict()
        return info
