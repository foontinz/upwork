import json
import requests
import bs4
from pprint import pprint


class Shelter:
    def __init__(self, shelter_id, shelter_name, shelter_address, shelter_coordinates, shelter_email, shelter_phone,
                 shelter_mission, shelter_adoption_policy, shelter_photos):
        self.unit = {
            'shelter_id': shelter_id,
            'shelter_name': shelter_name,
            'shelter_address': shelter_address,
            'shelter_coordinates': shelter_coordinates,
            'shelter_email': shelter_email,
            'shelter_phone': shelter_phone,
            'shelter_mission': shelter_mission,
            'shelter_adoption_policy': shelter_adoption_policy,
            'shelter_photos': shelter_photos
        }


class Pet:
    def __init__(self, pet_is_adopted, pet_id, pet_published_at, pet_name, pet_description, pet_attributes,
                 pet_adoption_fee, pet_about_attributes, pet_about_home_environment_attributes, pet_photos,
                 pet_shelter_name, pet_shelter_id, pet_shelter_location, pet_shelter_coordinates, pet_shelter_email,
                 pet_shelter_phone,
                 pet_shelter_link):
        self._unit = {'pet_is_adopted': pet_is_adopted,
                      'pet_id': pet_id,
                      'pet_published_at': pet_published_at,
                      'pet_name': pet_name,
                      'pet_description': pet_description,
                      'pet_attributes': pet_attributes,
                      'pet_adoption_fee': pet_adoption_fee,
                      'pet_about_attributes': pet_about_attributes,
                      'pet_about_home_environment_attributes': pet_about_home_environment_attributes,
                      'pet_photos': pet_photos,
                      'pet_shelter_id': pet_shelter_id,
                      'pet_shelter_name': pet_shelter_name,
                      'pet_shelter_location': pet_shelter_location,
                      'pet_shelter_coordinates': pet_shelter_coordinates,
                      'pet_shelter_email': pet_shelter_email,
                      'pet_shelter_phone': pet_shelter_phone,
                      'pet_shelter_link': pet_shelter_link}

    @property
    def unit(self):
        return self._unit


class Scraper:
    def __init__(self, link, instance, *args, **kwargs):
        self.link = link
        self.html = self.make_request()
        self.soup = self.make_soup()
        if instance.lower() == "pet":
            for script in self.soup.find_all("script"):
                if """global.PF.pageConfig = {""" in script.text.strip():
                    self.json_data_animal = (json.loads(
                        script.text.strip()[script.text.strip().find('{"user_auth"'):-11].strip()[:-2] + "}"))
                    self.object = self.get_pet_info()
        if instance.lower() == "shelter":
            self.object = self.get_shelter_info()

    def make_request(self):
        return requests.get(self.link)

    def make_soup(self):
        return bs4.BeautifulSoup(self.html.text, 'html.parser')

    def get_shelter_info(self):
        shelter_id = self.parse_shelter_id()
        shelter_name = self.parse_shelter_name()
        shelter_address = self.parse_shelter_location()
        shelter_coordinates = self.parse_shelter_coordinates()
        shelter_email = self.parse_shelter_email()
        shelter_phone = self.parse_shelter_phone()
        shelter_mission = self.parse_shelter_mission()
        shelter_adoption_policy = self.parse_shelter_adoption_policy()
        shelter_photos = self.parse_shelter_photos()
        return Shelter(shelter_id, shelter_name, shelter_address, shelter_coordinates, shelter_email, shelter_phone,
                       shelter_mission, shelter_adoption_policy, shelter_photos)

    def parse_shelter_id(self):
        try:
            if self.soup.find("span", {"itemprop": "telephone"}):
                return self.soup.find("span", {"itemprop": "telephone"}).findParent().findParent()['organization-id']
        except AttributeError:
            pass

    def parse_shelter_name(self):
        if self.soup.find("h1", {"itemprop": "name"}):
            return self.soup.find("h1", {"itemprop": "name"}).text.strip()

    def parse_shelter_location(self):
        shelter_location_section = self.soup.find("div", {"itemprop": "address"})
        shelter_location_street_address = shelter_location_section.find("div", {"itemprop": "streetAddress"})
        shelter_location_address_locality = shelter_location_section.find("span", {"itemprop": "addressLocality"})
        shelter_location_address_region = shelter_location_section.find("span", {"itemprop": "addressRegion"})
        shelter_location_postal_code = shelter_location_section.find("span", {"itemprop": "postalCode"})

        shelter_location_raw = {"streetAddress": shelter_location_street_address,
                                "addressLocality": shelter_location_address_locality,
                                "addressRegion": shelter_location_address_region,
                                "postalCode": shelter_location_postal_code}
        shelter_location = {}
        for key, value in shelter_location_raw.items():
            if value:
                shelter_location.update({key: value.text.strip()})
            else:
                shelter_location.update({key: value})
        return shelter_location

    def parse_shelter_coordinates(self):
        shelter_coordinates_section = self.soup.find("div", {"class": "get-directions"})
        if shelter_coordinates_section:
            shelter_coordinates = {"latitude": shelter_coordinates_section["data-latitude"].strip(),
                                   "longitude": shelter_coordinates_section["data-longitude"].strip()}
        else:
            shelter_coordinates = {"latitude": None,
                                   "longitude": None}
        return shelter_coordinates

    def parse_shelter_email(self):
        if self.soup.find("div", {"class": "tier-inner"}).select_one("a[href*=mailto]"):
            return self.soup.find("div", {"class": "tier-inner"}).select_one("a[href*=mailto]").text.strip()

    def parse_shelter_phone(self):
        if self.soup.find("span", {"itemprop": "telephone"}):
            return self.soup.find("span", {"itemprop": "telephone"}).text.strip()

    def parse_shelter_mission(self):
        try:
            for div in self.soup.find("div", {"class": "vrArray vrArray_divided m-vrArray_6x"}).find_all("div"):
                if div.find("h2").text.strip() == "Adoption Policy":
                    return div.find("p").text.strip()
        except AttributeError:
            pass

    def parse_shelter_adoption_policy(self):
        try:
            for div in self.soup.find("div", {"class": "vrArray vrArray_divided m-vrArray_6x"}).find_all("div"):
                if div.find("h2").text.strip() == "Our Mission":
                    return div.find("p").text.strip()
        except AttributeError:
            pass

    def parse_shelter_photos(self):
        try:
            raw_photos = self.soup.find("div", {"class": "card-section card-section_flush"}).find_all("img")
            if raw_photos:
                return [photo["src"] for photo in raw_photos]
        except AttributeError:
            pass

    def get_pet_info(self):  # pet
        pet_is_adopted = self.parse_pet_is_adopted()
        pet_id = self.parse_pet_id()
        pet_published_at = self.parse_pet_published_at()
        pet_name = self.parse_pet_name()
        pet_description = self.parse_pet_description()
        pet_attributes = self.parse_pet_attributes()
        pet_adoption_fee = self.parse_public_adoption_fee()
        pet_about_attributes = self.parse_pet_about_attributes()
        pet_about_home_environment_attributes = self.parse_pet_about_home_environment_attributes()
        pet_photos = self.parse_pet_photos()
        pet_shelter_name = self.parse_pet_shelter_name()
        pet_shelter_id = self.parse_pet_shelter_id()
        pet_shelter_location = self.parse_pet_shelter_location()
        pet_shelter_coordinates = self.parse_pet_shelter_coordinates()
        pet_shelter_email = self.parse_pet_shelter_email()
        pet_shelter_phone = self.parse_pet_shelter_phone()
        pet_shelter_link = self.parse_pet_shelter_link()
        return Pet(pet_is_adopted, pet_id, pet_published_at, pet_name, pet_description, pet_attributes,
                   pet_adoption_fee,
                   pet_about_attributes, pet_about_home_environment_attributes, pet_photos, pet_shelter_name,
                   pet_shelter_id, pet_shelter_location, pet_shelter_coordinates, pet_shelter_email,
                   pet_shelter_phone,
                   pet_shelter_link)

    def parse_pet_is_adopted(self):
        return self.json_data_animal['animal']['adoption_status']

    def parse_pet_id(self):
        return self.json_data_animal['animal']['id']

    def parse_pet_published_at(self):
        return self.json_data_animal['animal']['published_at']

    def parse_pet_name(self):
        if self.soup.find("span", {"data-test": "Pet_Name"}):
            return self.soup.find("span", {"data-test": "Pet_Name"}).text.strip()
        if self.json_data_animal["animal"]["name"]:
            return self.json_data_animal["animal"]["name"].strip()

    def parse_pet_description(self):
        try:
            if self.soup.find("div", {"data-test": "Pet_Story_Section"}).find("div", {"class": "u-vr4x"}):
                return self.soup.find("div", {"data-test": "Pet_Story_Section"}).find("div",
                                                                                      {"class": "u-vr4x"}).text.strip()
        except AttributeError:
            pass

        if self.json_data_animal['animal']["description"]:
            return self.json_data_animal['animal']["description"].strip()

    def parse_pet_attributes(self):
        return {
            "age": self.json_data_animal["animal"]['age'],
            "sex": self.json_data_animal["animal"]['sex'],
            "size": self.json_data_animal["animal"]['size'],
            "primary_color": self.json_data_animal["animal"]['primary_color'],
            "secondary_color": self.json_data_animal["animal"]['secondary_color'],
            "primary_breed": self.json_data_animal["animal"]['primary_breed'],
            "secondary_breed": self.json_data_animal["animal"]['secondary_breed']
        }

    def parse_public_adoption_fee(self):
        return self.json_data_animal['animal']['public_adoption_fee']

    def parse_pet_about_attributes(self):
        return self.json_data_animal['animal']['attributes']

    def parse_pet_about_home_environment_attributes(self):
        return self.json_data_animal['animal']['home_environment_attributes']

    def parse_pet_photos(self):
        return self.json_data_animal['animal']['photo_urls']

    def parse_pet_shelter_name(self):
        if self.soup.find("span", {"itemprop": "name"}):
            return self.soup.find("span", {"itemprop": "name"}).text.strip()
        return self.json_data_animal['organization']['name']

    def parse_pet_shelter_id(self):
        return self.json_data_animal['organization']['display_id']

    def parse_pet_shelter_location(self):
        return self.json_data_animal['location']['address']

    def parse_pet_shelter_coordinates(self):
        return self.json_data_animal['location']['geo']

    def parse_pet_shelter_email(self):
        return self.json_data_animal['contact']['email']

    def parse_pet_shelter_phone(self):
        return self.json_data_animal['contact']['phone']

    def parse_pet_shelter_link(self):
        if self.soup.find("a", {"class": "card_org-logo"}):
            return self.soup.find("a", {"class": "card_org-logo"})["href"].strip()


print(Scraper(
    "https://www.petfinder.com/member/us/ak/fairbanks/homeward-bound-pet-rescue-and-referral-ak29/",
    'shelter').object.unit)
