    
def scrape_professor_info(soup):
    prof_info = {}

    # Name
    name_tag = soup.find("h1")
    if name_tag:
        prof_info["Name"] = name_tag.get_text(strip=True)
    else:
        prof_info["Name"] = "Not Available"

    # Designation and Department
    # Designation & Department (combined)
    designation_block = None
    for span in soup.find_all("span"):
        if span.find("b") and "Professor" in span.get_text():
            designation_block = span.get_text(strip=True)
            break

    if designation_block:
        parts = designation_block.split(",", 1)
        prof_info["Designation"] = parts[0].strip()  # e.g., "Associate Professor"
        if len(parts) > 1:
            prof_info["Department"] = parts[1].strip()  # e.g., "Computer Science & Engineering"
    else:
        prof_info["Designation"] = "Not Available"
        prof_info["Department"] = "Not Available"


    # Education
    education = []
    lead_section = soup.find("p", class_="lead")
    if lead_section:
        edu_items = lead_section.find_all("li")
        for li in edu_items:
            education.append(li.get_text(strip=True))
    prof_info["Education"] = education

    # Email
    email_tag = soup.find("p", string=lambda t: t and "Email" in t)
    if not email_tag:
        email_tag = soup.find("p", text=lambda t: t and "Email" in t)
    if email_tag:
        prof_info["Email"] = email_tag.get_text(strip=True).replace("Email:", "").replace("-AT-", "@")

    # Office and VOIP
    office_voip = {}
    for p in soup.find_all("p"):
        if "Office:" in p.text:
            office_voip["Office"] = p.text.split("Office:")[1].strip().split("\n")[0].strip()
        if "VOIP:" in p.text:
            office_voip["VOIP"] = p.text.split("VOIP:")[1].strip().split("\n")[0].strip()
    prof_info["Office_Info"] = office_voip

    # Research Interests
    research_interests = []
    sidebar = soup.find("div", class_="sidebar__widget")
    if sidebar:
        li_tags = sidebar.find_all("li")
        research_interests = [li.get_text(strip=True).replace("● ", "") for li in li_tags]
    prof_info["Research Interests"] = research_interests

    # Publications
    publications = []
    pub_section = soup.find("span", string="Selected Publications")
    if pub_section:
        pub_list = pub_section.find_parent("li").find("ol")
        if pub_list:
            for li in pub_list.find_all("li"):
                publications.append(li.get_text(strip=True))
    prof_info["Publications"] = publications

    # Work Experience
    experience = []
    exp_section = soup.find("span", string="Work Experience")
    if exp_section:
        exp_list = exp_section.find_parent("li").find("ul")
        if exp_list:
            for li in exp_list.find_all("li"):
                experience.append(li.get_text(strip=True))
    prof_info["Experience"] = experience

    email_text = ""
    for p in soup.find_all("p"):
        if "Email" in p.get_text():
            email_text = p.get_text(strip=True)
            break

    import re

    if email_text:
        # Extract email using regex, accounting for "-AT-" replacement
        match = re.search(r"Email[:\s]*([\w\.-]+)\s*-AT-\s*([\w\.-]+)", email_text)
        if match:
            prof_info["Email"] = f"{match.group(1)}@{match.group(2)}"
        else:
            # If regex fails, fallback to the original email extraction
            prof_info["Email"] = email_text.replace("Email:", "").replace("-AT-", "@").strip()

    else:
        prof_info["Email"] = "Not Available"


    return prof_info