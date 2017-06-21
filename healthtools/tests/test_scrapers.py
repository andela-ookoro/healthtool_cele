import unittest
import requests
import json
from healthtools.scrapers.base_scraper import Scraper
from healthtools.scrapers.doctors import DoctorsScraper
from healthtools.scrapers.foreign_doctors import ForeignDoctorsScraper
from healthtools.scrapers.clinical_officers import ClinicalOfficersScraper
from healthtools.scrapers.health_facilities import HealthFacilitiesScraper
from healthtools.config import TEST_DIR, SLACK


class TestDoctorsScraper(unittest.TestCase):
    def setUp(self):
        self.base_scraper = Scraper()
        self.doctors_scraper = DoctorsScraper()
        self.foreign_doctors_scraper = ForeignDoctorsScraper()
        self.clinical_officers_scraper = ClinicalOfficersScraper()
        self.health_facilities_scraper = HealthFacilitiesScraper()

    def test_it_gets_the_total_number_of_pages(self):
        self.doctors_scraper.get_total_number_of_pages()
        self.assertIsNotNone(self.doctors_scraper.num_pages_to_scrape)

    def test_it_scrapes_doctors_page(self):
        entries = self.doctors_scraper.scrape_page(
            "http://medicalboard.co.ke/online-services/retention/?currpage=1")[0]
        self.assertTrue(len(entries) == 60)

    def test_it_scrapes_foreign_doctors_page(self):
        entries = self.foreign_doctors_scraper.scrape_page(
            "http://medicalboard.co.ke/online-services/foreign-doctors-license-register/?currpage=1")[0]
        self.assertTrue(len(entries) == 60)

    def test_it_scrapes_clinical_officers_page(self):
        entries = self.clinical_officers_scraper.scrape_page(
            "http://clinicalofficerscouncil.org/online-services/retention/?currpage=1")[0]
        self.assertTrue(len(entries) == 60)

    def test_doctors_scraper_uploads_to_elasticsearch(self):
        with open(TEST_DIR + "/dummy_files/doctors.json", "r") as my_file:
            data = my_file.read()
            self.doctors_scraper.delete_elasticsearch_docs()
            response = self.doctors_scraper.upload_data(json.loads(data))
            self.assertEqual(response['items'][0]['index']['status'], 201)

    def test_foreign_doctors_scraper_uploads_to_elasticsearch(self):
        with open(TEST_DIR + "/dummy_files/foreign_doctors.json", "r") as my_file:
            data = my_file.read()
            self.foreign_doctors_scraper.delete_elasticsearch_docs()
            response = self.foreign_doctors_scraper.upload_data(json.loads(data))
            self.assertEqual(response['items'][0]['index']['status'], 200)

    def test_clinical_officers_scraper_uploads_to_elasticsearch(self):
        with open(TEST_DIR + "/dummy_files/clinical_officers.json", "r") as my_file:
            data = my_file.read()
            self.clinical_officers_scraper.delete_elasticsearch_docs()
            response = self.clinical_officers_scraper.upload_data(json.loads(data))
            self.assertEqual(response['items'][0]['index']['status'], 201)

    def test_health_facilities_scraper_uploads_to_elasticsearch(self):
        with open(TEST_DIR + "/dummy_files/health_facilities.json", "r") as my_file:
            data = my_file.read()
            self.health_facilities_scraper.delete_elasticsearch_docs()
            response = self.health_facilities_scraper.upload(json.loads(data))
            self.assertEqual(response['items'][0]['index']['status'], 201)

    def test_doctors_scraper_archives_to_s3(self):
        self.doctors_scraper.s3_key = "test/doctors.json"
        with open(TEST_DIR + "/dummy_files/doctors.json", "r") as my_file:
            data = my_file.read()
            self.doctors_scraper.archive_data(data)
        uploaded_data = self.doctors_scraper.s3.get_object(
            Bucket="cfa-healthtools-ke",
            Key=self.doctors_scraper.s3_key
            )['Body'].read()
        self.assertEqual(uploaded_data, data)

    def test_foreign_doctors_scraper_archives_to_s3(self):
        self.foreign_doctors_scraper.s3_key = "test/foreign_doctors.json"
        with open(TEST_DIR + "/dummy_files/foreign_doctors.json", "r") as my_file:
            data = my_file.read()
            self.foreign_doctors_scraper.archive_data(data)
        uploaded_data = self.foreign_doctors_scraper.s3.get_object(
            Bucket="cfa-healthtools-ke",
            Key=self.foreign_doctors_scraper.s3_key
            )['Body'].read()
        self.assertEqual(uploaded_data, data)

    def test_clinical_officers_scraper_archives_to_s3(self):
        self.clinical_officers_scraper.s3_key = "test/clinical_officers.json"
        with open(TEST_DIR + "/dummy_files/clinical_officers.json", "r") as my_file:
            data = my_file.read()
            self.clinical_officers_scraper.archive_data(data)
        uploaded_data = self.clinical_officers_scraper.s3.get_object(
            Bucket="cfa-healthtools-ke",
            Key=self.clinical_officers_scraper.s3_key
            )['Body'].read()
        self.assertEqual(uploaded_data, data)

    def test_health_facilities_scraper_gets_token(self):
        self.health_facilities_scraper.get_token()
        self.assertIsNotNone(self.health_facilities_scraper.access_token)

    def test_scrapper_sends_slack_notification(self):
        response = self.base_scraper.post_to_slack("Tests are passing")
        self.assertEqual(response.status_code, 200)
