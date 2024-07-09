import os
import time

from crewai_tools import tool
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from tools.utils import get_linkedin_posts,get_linkedin_post


class LinkedinToolException(Exception):
    def __init__(self):
        super().__init__("You need to set the LINKEDIN_EMAIL and LINKEDIN_PASSWORD env variables")


def scrape_linkedin_posts_fn(profile_username: str,orglink: int) -> str:
    print(f"Received profile_url in tool: {profile_username!r}")
    """
    A tool that can be used to scrape LinkedIn posts
    
    """
    linkedin_username = os.environ.get("LINKEDIN_EMAIL")
    linkedin_password = os.environ.get("LINKEDIN_PASSWORD")
    linkedin_profile_name = os.environ.get("LINKEDIN_PROFILE_NAME")

    if not (linkedin_username and linkedin_password):
        raise LinkedinToolException()

    browser = webdriver.Chrome()
    browser.get("https://www.linkedin.com/login")

    username_input = browser.find_element("id", "username")
    password_input = browser.find_element("id", "password")
    username_input.send_keys(linkedin_username)
    password_input.send_keys(linkedin_password)
    password_input.send_keys(Keys.RETURN)

    time.sleep(10)
    if orglink==0:
        browser.get(f"https://www.linkedin.com/in/{profile_username}/recent-activity/all/")
    else:
        browser.get(f"https://www.linkedin.com/company/{profile_username}/posts/")
    time.sleep(2)
    for _ in range(2):
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    posts = get_linkedin_posts(browser.page_source)
    browser.quit()

    # We'll just return 2 of the latest posts, since it should be enough for the LLM to get the overall style
    return str(posts[:2])

#Creating our custom tool here
@tool("ScrapeLinkedinPosts")
def scrape_linkedin_posts_tool(input_dict: dict) -> str:
    
    """
    A tool that scrapes LinkedIn posts from a given profile URL.
    """
    profile_username = input_dict.get("profile")
    org_num = input_dict.get("orglink")
    if not profile_username:
        raise ValueError("Profile username not provided")
    return scrape_linkedin_posts_fn(profile_username,org_num)













#Referal Post scrape

def scrape_single_linkedin_post_fn(link: str) -> str:
    print(f"Received profile_url in tool: {link!r}")
    """
    A tool that can be used to scrape a single LinkedIn post
    
    """
    linkedin_username = os.environ.get("LINKEDIN_EMAIL")
    linkedin_password = os.environ.get("LINKEDIN_PASSWORD")
    linkedin_profile_name = os.environ.get("LINKEDIN_PROFILE_NAME")

    if not (linkedin_username and linkedin_password):
        raise LinkedinToolException()

    browser = webdriver.Chrome()
    browser.get("https://www.linkedin.com/login")

    username_input = browser.find_element("id", "username")
    password_input = browser.find_element("id", "password")
    username_input.send_keys(linkedin_username)
    password_input.send_keys(linkedin_password)
    password_input.send_keys(Keys.RETURN)

    time.sleep(10)
    
    browser.get(link)

    # for _ in range(2):
    #     browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    #     time.sleep(2)

    post = get_linkedin_post(browser.page_source)
    browser.quit()

   #Return the single post
    return str(post[0])


#Creating our custom tool here 2
@tool("ScrapeLinkedinPost")
def scrape_single_linkedin_post_tool(link: str) -> str:
    
    """
    A tool that scrapes LinkedIn posts from a given profile URL.
    """
    profile_post = link.get("link")
    if not profile_post:
        raise ValueError("Profile link not provided")
    return scrape_single_linkedin_post_fn(profile_post)