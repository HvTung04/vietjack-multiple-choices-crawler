import requests
from bs4 import BeautifulSoup
import json


def fetch_quest(soup, site):
    if site == "vietjack_com":
        return fetch_quest_vietjack_com(soup)
    if site == "vietjack_me":
        return fetch_quest_vietjack_me(soup)


def export_all_href(url, site):
    if site == "vietjack_com":
        return export_all_href_vietjack_com(url)
    if site == "vietjack_me":
        return export_all_href_vietjack_me(url)
    return None


def export_all_href_vietjack_com(url):
    soup = fetch_soup(url)
    hrefs = soup.find_all("a")
    url_list = [href.get("href") for href in hrefs]
    url_list = [
        f"https://vietjack.com/{url}"
        for url in url_list
        if isinstance(url, str)
        and url.startswith("../")
        and url.endswith(".jsp")
        and "bai-tap-trac-nghiem" in url
        and "index" not in url
        and not url.split("/")[-1].startswith("chuong-")
    ]
    return url_list


def export_all_href_vietjack_me(url):
    soup = fetch_soup(url)
    hrefs = soup.find_all("a")
    url_list = [href.get("href") for href in hrefs]
    url_list = [
        url
        for url in url_list
        if isinstance(url, str) and url.startswith("https://") and url.endswith(".html")
    ]
    return url_list


def extract_json_template(input_string):
    """
    Extracts a JSON object from a larger string containing the JSON object.

    Parameters:
    - input_string (str): The input string containing the JSON object.

    Returns:
    - dict: A dictionary representation of the extracted JSON object, or None if extraction fails.
    """
    try:
        # Find the start and end of the JSON object
        start_index = input_string.find("{")
        end_index = input_string.rfind("}") + 1  # Include the closing brace

        # Extract the JSON string
        json_string = input_string[start_index:end_index]

        # Parse the JSON string into a Python dictionary
        json_object = json.loads(json_string)

        return json_object
    except ValueError as e:
        print(f"Error extracting or parsing JSON: {e}")
        print("--------------ERROR-------------------")
        print(f"Input string: {json_string}")
        print("---------------------------------\n\n")
        return None


def fetch_soup(url):
    response = requests.get(url)
    html_content = response.text

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")
    return soup


def elements_in_between(start_element, end_element):
    elements_in_between = []
    for sibling in start_element.next_siblings:
        if sibling == end_element:
            break
        if sibling.name:
            elements_in_between.append(sibling)
    return elements_in_between


def elements_in_between(start_element, end_element):
    elements_in_between = []
    for sibling in start_element.next_siblings:
        if sibling == end_element or str(end_element) in str(sibling):
            break
        if sibling.name and sibling.name == "p":
            elements_in_between.append(sibling)
    return elements_in_between


def split_choices_string(choice_elements: str):
    A_string = choice_elements.split("A.")[1].split("B.")[0]
    B_string = choice_elements.split("B.")[1].split("C.")[0]
    C_string = choice_elements.split("C.")[1].split("D.")[0]
    D_string = choice_elements.split("D.")[1]
    return {"choice_A": A_string, "choice_B": B_string, "choice_C": C_string, "choice_D": D_string}


def split_choices(elements_between):
    state = {
        "question": {"content": "", "done": False},
        "choice_A": {"content": "", "done": False},
        "choice_B": {"content": "", "done": False},
        "choice_C": {"content": "", "done": False},
        "choice_D": {"content": "", "done": False},
    }
    current_choice = "question"
    for element in elements_between:
        if "A." in element.text and not state["choice_A"]["done"]:
            current_choice = "choice_A"
            state["question"]["done"] = True
        if "B." in element.text and not state["choice_B"]["done"]:
            current_choice = "choice_B"
            state["choice_A"]["done"] = True
        if "C." in element.text and not state["choice_C"]["done"]:
            current_choice = "choice_C"
            state["choice_B"]["done"] = True
        if "D." in element.text and not state["choice_D"]["done"]:
            current_choice = "choice_D"
            state["choice_C"]["done"] = True
        state[current_choice]["content"] += str(element) + "\n"
    state["choice_D"]["done"] = True
    return state


def fetch_quest_vietjack_me(soup):
    content_div = soup.find("div", id="content-post")
    answer_section = content_div.find_all("section", {"class": "vj-template-answer"})

    # Get for first question
    first_question = answer_section[0].findPreviousSiblings(
        "p", {"style": "text-align: justify;"}
    )
    first_comps = first_question[::-1]
    quest = split_choices(first_comps)

    # Init question_data
    question_data = [
        {
            "question": quest["question"]["content"],
            "A": quest["choice_A"]["content"],
            "B": quest["choice_B"]["content"],
            "C": quest["choice_C"]["content"],
            "D": quest["choice_D"]["content"],
            "answer": str(answer_section[0]),
        }
    ]

    for i, answer in enumerate(answer_section[1:]):
        comps = elements_in_between(answer_section[i - 1], answer)
        if len(comps) == 0:
            continue
        try:
            quest = split_choices(comps)
            data = {
                "question": quest["question"]["content"],
                "A": quest["choice_A"]["content"],
                "B": quest["choice_B"]["content"],
                "C": quest["choice_C"]["content"],
                "D": quest["choice_D"]["content"],
                "answer": str(answer),
            }
            question_data.append(data)
        except Exception as e:
            print(f"Error fetching question: {e}")
            print("--------------ERROR-------------------")
            print(f"Answer: {str(answer)}")
            print("---------------------------------\n\n")
            continue
    return question_data


def fetch_quest_vietjack_com(soup):
    start_tag = soup.find("div", class_="ads_ads ads_1")

    answer_tags = soup.find_all("section", {"class": "toggle"})   # List of answers
    questions_data = []
    for i, tag in enumerate(answer_tags):
        if i == 0:
            continue
        try:
            question_tag = answer_tags[i-1].find_next_sibling("p")
            choices_tags = elements_in_between(question_tag, tag)
            choices_section = split_choices_string("".join([str(tag) for tag in choices_tags]))

            data = {
                "question": question_tag,
                "A": choices_section["choice_A"],
                "B": choices_section["choice_B"],
                "C": choices_section["choice_C"],
                "D": choices_section["choice_D"],
                "answer": tag,
            }
            questions_data.append(data)
        except Exception as e:
            print(f"Error fetching question: {e}")
            print("--------------ERROR-------------------")
            print(f"Question tag: {question_tag}")
            print(f"Choices tags: {choices_tags}")
            print("---------------------------------\n\n")
            continue

    return questions_data
