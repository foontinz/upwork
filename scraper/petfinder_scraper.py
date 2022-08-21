import json
from pprint import pprint

import bs4
import requests


class Shelter:
    def __init__(self, shelter_id, shelter_name, shelter_address, shelter_coordinates, shelter_email, shelter_phone,
                 shelter_mission, shelter_adoption_policy, shelter_photos):
        self._unit = {
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

    @property
    def unit(self):
        return self._unit


class Pet:
    def __init__(self, pet_is_adopted, pet_id, pet_published_at, pet_name, pet_description, pet_tags, pet_attributes,
                 pet_adoption_fee, pet_about_attributes, pet_about_home_environment_attributes, pet_photos,
                 pet_shelter_name, pet_shelter_id, pet_shelter_location, pet_shelter_coordinates, pet_shelter_email,
                 pet_shelter_phone,
                 pet_shelter_link):
        self._unit = {'pet_is_adopted': pet_is_adopted,
                      'pet_id': pet_id,
                      'pet_published_at': pet_published_at,
                      'pet_name': pet_name,
                      'pet_description': pet_description,
                      'pet_tags': pet_tags,
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
            try:
                for script in self.soup.find_all("script"):
                    if """global.PF.pageConfig = {""" in script.text.strip():
                        self.json_data_animal = (json.loads(
                            script.text.strip()[script.text.strip().find('{"user_auth"'):-11].strip()[:-2] + "}"))
                        self.json_data_animal['animal']['home_environment_attributes'].pop("other_animals", None)

                        self.object = self.get_pet_info()
            except AttributeError or Exception:
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
        pet_tags = self.parse_pet_tags()
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
        return Pet(pet_is_adopted, pet_id, pet_published_at, pet_name, pet_description, pet_tags, pet_attributes,
                   pet_adoption_fee,
                   pet_about_attributes, pet_about_home_environment_attributes, pet_photos, pet_shelter_name,
                   pet_shelter_id, pet_shelter_location, pet_shelter_coordinates, pet_shelter_email,
                   pet_shelter_phone,
                   pet_shelter_link)

    def parse_pet_is_adopted(self):
        try:
            return self.json_data_animal['animal']['adoption_status']
        except AttributeError or Exception:
            return self.soup.find("p", {"id": "Pet_Carousel_Description"}).findParent()['animal-status']

    def parse_pet_id(self):
        try:
            return self.json_data_animal['animal']['id']
        except AttributeError or Exception:
            return self.soup.find("p", {"id": "Pet_Carousel_Description"}).findParent()['animal_id']

    def parse_pet_published_at(self):
        try:
            return self.json_data_animal['animal']['published_at']
        except AttributeError or Exception:
            return

    def parse_pet_name(self):
        try:
            return self.json_data_animal["animal"]["name"].strip()
        except AttributeError or Exception:
            return self.soup.find("span", {"data-test": "Pet_Name"}).text.strip()

    def parse_pet_description(self):
        try:
            if self.soup.find("div", {"data-test": "Pet_Story_Section"}).find("div", {"class": "u-vr4x"}):
                return self.soup.find("div", {"data-test": "Pet_Story_Section"}).find("div",
                                                                                      {"class": "u-vr4x"}).text.strip()
        except AttributeError or Exception:
            return

    def parse_pet_attributes(self):
        return {
            "age": self.parse_pet_age(),
            "sex": self.parse_pet_sex(),
            "size": self.parse_pet_size(),
            "primary_color": self.parse_pet_primary_color(),
            "secondary_color": self.parse_pet_secondary_color(),
            "primary_breed": self.parse_pet_primary_breed(),
            "secondary_breed": self.parse_pet_secondary_breed()
        }

    def parse_pet_age(self):
        try:
            return self.json_data_animal["animal"]['age']
        except AttributeError or Exception:
            try:
                return self.soup.find("span", {"data-test": "Pet_Age"}).text.strip()
            except AttributeError or Exception:
                return

    def parse_pet_sex(self):
        try:
            return self.json_data_animal["animal"]['sex']
        except AttributeError or Exception:
            try:
                return self.soup.find("span", {"data-test": "Pet_Sex"}).text.strip()
            except AttributeError or Exception:
                return

    def parse_pet_size(self):
        try:
            return self.json_data_animal["animal"]['size']
        except AttributeError or Exception:
            try:
                return self.soup.find("span", {"data-test": "Pet_Full_Grown_Size"}).text.strip()
            except AttributeError or Exception:
                return

    def parse_pet_primary_color(self):
        try:
            return self.json_data_animal["animal"]['primary_color']
        except AttributeError or Exception:
            try:
                return self.soup.find("span", {"data-test": "Pet_Primary_Color"}).text.strip()
            except AttributeError or Exception:
                return

    def parse_pet_secondary_color(self):
        try:
            return self.json_data_animal["animal"]['secondary_color']
        except AttributeError or Exception:
            return

    def parse_pet_primary_breed(self):
        try:
            return self.json_data_animal["animal"]['primary_breed']
        except AttributeError or Exception:
            try:
                return self.soup.find("span", {"data-test": "Pet_Breeds"}).text.strip()
            except AttributeError or Exception:
                return

    def parse_pet_secondary_breed(self):
        try:
            return self.json_data_animal["animal"]['secondary_breed']
        except AttributeError or Exception:
            return

    def parse_public_adoption_fee(self):
        try:
            return self.json_data_animal['animal']['public_adoption_fee']
        except AttributeError or Exception:
            try:
                return int(float(self.soup.find("dt", string="Adoption fee").findParent().find("dd").text[1:]))
            except AttributeError or Exception:
                return

    def parse_pet_tags(self):
        try:
            return self.json_data_animal['animal']['tags']
        except AttributeError or Exception:
            try:
                return self.soup.find("dt", string='Characteristics').findParent().findChildren()[
                    self.soup.find("dt", string='Characteristics').findParent().findChildren().index(
                        self.soup.find("dt", string='Characteristics')) + 1].text.split(',')
            except AttributeError or Exception:
                return

    def parse_pet_about_attributes(self):
        try:
            coat_length = self.soup.find("dt", string='Coat length').findParent().findChildren()[
                self.soup.find("dt", string='Coat length').findParent().findChildren().index(
                    self.soup.find("dt", string='Coat length')) + 1].text
            house_trained = self.soup.find("dt", string='House-trained').findParent().findChildren()[
                self.soup.find("dt", string='House-trained').findParent().findChildren().index(
                    self.soup.find("dt", string='House-trained')) + 1].text
            health = self.soup.find("dt", string='Health').findParent().findChildren()[
                self.soup.find("dt", string='Health').findParent().findChildren().index(
                    self.soup.find("dt", string='Health')) + 1].text
            return {
                'Coat-length': coat_length,
                'House-trained': house_trained,
                'Health': health
            }
        except AttributeError or Exception:
            return {
                'Coat-length': None,
                'House-trained': None,
                'Health': None
            }

    def parse_pet_about_home_environment_attributes(self):
        try:
            return self.json_data_animal['animal']['home_environment_attributes']
        except AttributeError or Exception:
            try:
                good_with = self.soup.find("dt", string='Good in a home with').findParent().findChildren()[
                    self.soup.find("dt",
                                   string='Good in a home with').findParent().findChildren().index(
                        self.soup.find("dt", string='Good in a home with')) + 1].text.lower()
            except AttributeError or Exception:
                good_with = None

            try:
                bad_with = self.soup.find("dt", string='Prefers a home without').findParent().findChildren()[
                    self.soup.find("dt",
                                   string='Prefers a home without').findParent().findChildren().index(
                        self.soup.find("dt", string='Prefers a home without')) + 1].text.lower()
            except AttributeError or Exception:
                bad_with = None

            good_with_cats = None
            good_with_children = None
            good_with_dogs = None
            good_with_other_animals = None

            if good_with:
                good_with_cats = True if "cats" in good_with else None
                good_with_children = True if "children" in good_with else None
                good_with_dogs = True if "dogs" in good_with else None
                good_with_other_animals = True if "animals" in good_with else None
            if bad_with:
                good_with_cats = False if not good_with_cats and "cats" in bad_with else None
                good_with_children = False if not good_with_children and "children" in bad_with else None
                good_with_dogs = False if not good_with_dogs and "dogs" in bad_with else None
                good_with_other_animals = False if not good_with_other_animals and "animals" in bad_with else None

            return {'good_with_cats': good_with_cats,
                    'good_with_children': good_with_children,
                    'good_with_dogs': good_with_dogs,
                    'good_with_other_animals': good_with_other_animals}

    def parse_pet_photos(self):
        try:
            return self.json_data_animal['animal']['photo_urls']
        except AttributeError or Exception:
            try:
                raw_photos = self.soup.find("div", {"role": "main"}).find("div",
                                                                          {"class": "petCarousel-body"}).find_all("img")
                if raw_photos:
                    photos = [photo["src"] for photo in raw_photos]
                    return photos
            except AttributeError or Exception:
                return []

    def parse_pet_shelter_name(self):
        try:
            return self.json_data_animal['organization']['name']
        except AttributeError or Exception:
            try:
                return self.soup.find("span", {"itemprop": "name"}).text.strip()
            except AttributeError or Exception:
                return

    def parse_pet_shelter_id(self):
        try:
            return self.json_data_animal['organization']['display_id']
        except AttributeError or Exception:
            return self.link[self.link.rfind('-') + 1:-1].upper()

    def parse_pet_shelter_location(self):
        return {'address': self.parse_pet_shelter_location_address(),
                'city': self.parse_pet_shelter_location_city(),
                'postal_code': self.parse_pet_shelter_location_postal_code(),
                'state': self.parse_pet_shelter_location_state()}

    def parse_pet_shelter_location_address(self):
        try:
            return self.json_data_animal['location']['address']['address1']
        except AttributeError or Exception:
            try:
                return self.soup.find("div", {"class": "txt", "itemprop": "streetAddress"}).text
            except AttributeError or Exception:
                return

    def parse_pet_shelter_location_city(self):
        try:
            return self.json_data_animal['location']['address']['city']
        except AttributeError or Exception:
            try:
                return self.soup.find("span", {"class": "txt", "itemprop": "addressLocality"}).text
            except AttributeError or Exception:
                return

    def parse_pet_shelter_location_postal_code(self):
        try:
            return self.json_data_animal['location']['address']['postal_code']
        except AttributeError or Exception:
            try:
                return self.soup.find("span", {"class": "txt", "itemprop": "postalCode"}).text
            except AttributeError or Exception:
                return

    def parse_pet_shelter_location_state(self):
        try:
            return self.json_data_animal['location']['address']['state']
        except AttributeError or Exception:
            try:
                return self.soup.find("span", {"class": "txt", "itemprop": "addressRegion"}).text
            except AttributeError or Exception:
                return

    def parse_pet_shelter_coordinates(self):
        try:
            return self.json_data_animal['location']['geo']
        except AttributeError or Exception:
            shelter_coordinates_section = self.soup.find("div", {"class": "get-directions"})
            return {
                "latitude": shelter_coordinates_section[
                    "data-latitude"].strip() if shelter_coordinates_section else None,
                "longitude": shelter_coordinates_section[
                    "data-longitude"].strip() if shelter_coordinates_section else None}

    def parse_pet_shelter_email(self):
        try:
            return self.json_data_animal['contact']['email']
        except AttributeError or Exception:
            try:
                return self.soup.find("div", {"class": "card-section card-section_constrained"}).select_one(
                    "a[href*=mailto]").text.strip()
            except AttributeError or Exception:
                return

    def parse_pet_shelter_phone(self):
        try:
            return self.json_data_animal['contact']['phone']
        except AttributeError or Exception:
            try:
                return self.soup.find("span", {"itemprop": "telephone"}).text.strip()
            except AttributeError or Exception:
                return

    def parse_pet_shelter_link(self):
        try:
            return self.soup.find("a", {"class": "card_org-logo"})["href"].strip()
        except AttributeError or Exception:
            return


pprint(
    Scraper("https://www.petfinder.com/dog/hunter-55309697/ak/fairbanks/homeward-bound-pet-rescue-and-referral-ak29/",
            "pet").object.unit)
