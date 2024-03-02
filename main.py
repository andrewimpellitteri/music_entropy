import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import os

def scrape_composers_with_pages(base_url):
    url = urljoin(base_url, "classic.htm")
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    composer_info_mapping = {}
    composer_tags = soup.find_all("font", size="3")
    years_pattern = re.compile(r"\((\d{4})-(\d{4})\)")

    for composer_tag in composer_tags:
        composer_name = composer_tag.text.strip()[:-1]
        years_match = years_pattern.search(composer_tag.next_sibling.strip())
        if years_match:
            years_start = years_match.group(1)
            years_end = years_match.group(2)
            composer_years = f"{years_start}-{years_end}"
        else:
            composer_years = None

        composer_link = composer_tag.find_next("a", href=True)
        if composer_link:
            composer_page_url = urljoin(base_url, composer_link["href"])
            composer_page_response = requests.get(composer_page_url)
            composer_page_soup = BeautifulSoup(composer_page_response.content, "html.parser")
            midi_files = []
            midi_links = composer_page_soup.find_all("a", href=True)
            for midi_link in midi_links:
                midi_file_name = midi_link.text.strip()
                midi_file_url = urljoin(base_url, midi_link["href"])
                if midi_file_url.endswith(".mid"):
                    midi_files.append({"name": midi_file_name, "url": midi_file_url})
        else:
            midi_files = []

        composer_info_mapping[composer_name] = {"years": composer_years, "midi_files": midi_files}

    return composer_info_mapping

def scrape_composers_on_page(base_url):
    url = urljoin(base_url, "classic.htm")
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    composer_info_mapping = {}
    composer_tags = soup.find_all("font", size="3")
    years_pattern = re.compile(r"\((\d{4})-(\d{4})\)")

    for composer_tag in composer_tags:
        composer_name = composer_tag.text.strip()[:-1]
        years_match = years_pattern.search(composer_tag.next_sibling.strip())
        if years_match:
            years_start = years_match.group(1)
            years_end = years_match.group(2)
            composer_years = f"{years_start}-{years_end}"
        else:
            composer_years = None

        midi_files = []
        midi_links = composer_tag.find_next("ul").find_all("a", href=True)
        for midi_link in midi_links:
            midi_file_name = midi_link.text.strip()
            midi_file_url = urljoin(base_url, midi_link["href"])
            if midi_file_url.endswith(".mid"):
                midi_files.append({"name": midi_file_name, "url": midi_file_url})

        composer_info_mapping[composer_name] = {"years": composer_years, "midi_files": midi_files}

    return composer_info_mapping

def combine_dicts(dict1, dict2):
    combined_dict = dict1.copy()
    for key, value in dict2.items():
        if key in combined_dict:
            combined_dict[key]["midi_files"].extend(value["midi_files"])
        else:
            combined_dict[key] = value
    return combined_dict

def save_dict_to_file(data, filename):
    with open(filename, "w") as file:
        for composer, info in data.items():
            file.write(f"Composer: {composer}\n")
            file.write(f"Years Lived: {info['years']}\n")
            for midi_file in info["midi_files"]:
                file.write(f"\tName: {midi_file['name']}\n")
                file.write(f"\tURL: {midi_file['url']}\n")
            file.write("\n")

def download_files(data, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for composer, info in data.items():
        composer_dir = os.path.join(output_dir, composer.replace(" ", "_"))
        if not os.path.exists(composer_dir):
            os.makedirs(composer_dir)
        for midi_file in info["midi_files"]:
            filename = os.path.join(composer_dir, midi_file["name"] + ".mid")
            try:
                with open(filename, "wb") as file:
                    response = requests.get(midi_file["url"])
                    if response.status_code == 200:
                        file.write(response.content)
                    else:
                        print(f"Failed to download {midi_file['url']}. Status code: {response.status_code}")
            except FileNotFoundError:
                print(f"Error: Directory '{composer_dir}' does not exist.")
                continue

base_url = "https://www.midiworld.com/"
composers_with_pages = scrape_composers_with_pages(base_url)
composers_on_page = scrape_composers_on_page(base_url)
all_composers = combine_dicts(composers_with_pages, composers_on_page)

save_dict_to_file(all_composers, "composers_data.txt")
download_files(all_composers, "data")
