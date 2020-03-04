import requests
from bs4 import BeautifulSoup
import time
from colorama import init as init_colors
import json
from getpass import getpass

# Credentials [fill it instead for auto signing in]
username = input("Student's ID [6 digits]: ") + "@edu.p.lodz.pl"
password = getpass("Password [hidden]: ")

# Semester selection [fill it instead for auto choosing semester]
semester = input("Semester [digit or skip if you want the newest]: ")
try:
    semester = int(semester) - 1
except ValueError:
    semester = -1

# Initialization of colors from colorama
init_colors()

start = time.time()
with requests.Session() as s:
    url = "https://portal.wee.p.lodz.pl/"

    # Handling redirection
    r = s.head(url, allow_redirects=True)

    # Changing url to redirected url
    url = r.url

    # Heading to login page
    r = s.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

    # Finding attribute 'lt' which is crucial to post login credentials
    lt = soup.find('input', attrs={'name': 'lt'})['value']

    # Filling credentials
    credentials_names = ["username", "password", "submit", "lt", "_eventId"]
    credentials = dict(zip(credentials_names, [username, password, "LOGIN", lt, "submit"]))

    # Posting a request with credentials
    r = s.post(url, data=credentials)
    soup = BeautifulSoup(r.content, 'html.parser')

    # Finding "a href" with links to each semester
    a_tags = soup.find_all('a')
    a_hrefs = [a_tag.get('href') for a_tag in a_tags]

    # Semester links: ?page=indeks&sc...
    semester_links = [href for href in a_hrefs if href.startswith('?page=indeks')]
    semester_count = len(semester_links)
    semester_links = semester_links[semester_count//2:]

    # Extending current url with given semester url
    url = r.url + semester_links[semester]

    # Getting request from server
    r = s.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

    # Getting table containing all names data
    tables = soup.find_all("table", attrs={"class": "grid", "cellspacing": "0", "cellpadding": "0",
                                           "style": "width: 100%; margin-left: auto; margin-right: auto;"})

    # Extracting names of lecturers and tutors
    names_list = [table.find_all("td", attrs={"class": "left"}) for table in tables]
    names_list = [[name.text for name in names] for names in names_list]


    # Extracting marks
    tbodies = soup.find_all("tbody")[1:]
    marks_list = [tbody.find_all("strong") for tbody in tbodies]
    marks_list = [[mark.text for mark in marks] for marks in marks_list]

    # Extracting subjects
    subjects = soup.find_all("td", attrs={"class": "lcell left"})[1::2]
    subjects = [subject.text for subject in subjects]

    # Dictionary: key=subject, value={keys=lecturer/tutor, value=marks}
    summary = {}
    for i in range(len(names_list)):
        # Subject is taught only by a lecturer or tutor
        if len(names_list[i]) == 1:
            summary[subjects[i]] = {names_list[i][0]: marks_list[i][:4]}
        # Subject is taught by lecturer and tutor
        if len(names_list[i]) == 2:
            summary[subjects[i]] = {names_list[i][0]: marks_list[i][:4], names_list[i][1]: marks_list[i][4:]}

    # Displaying summary
    print("\033[91mWykaz ocen:\033[00m")
    for key in summary.keys():
        print(f"\033[92m{key}\033[00m")
        for name in summary[key]:
            marks = [mark for mark in summary[key][name] if mark]
            print(f"\t{name}", end='')
            if marks:
                print(f": {marks}")
            else:
                print()

end = time.time()
print(f"\nCzas generowania wykazu ocen: \033[91m{end-start:.2f} seconds\033[00m")


