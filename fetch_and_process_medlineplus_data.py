import requests
import zipfile
import io
import psycopg2
import os
import xml.etree.ElementTree as ET


# Database configuration from environment variables
db_config = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD")
}
# db_config = {
#     "host": "localhost",
#     "port": "5434",
#     "database": "medlineplus",
#     "user": "postgres",
#     "password": "postgres"
# }


def download_file(url):
    response = requests.get(url)
    response.raise_for_status()
    return io.BytesIO(response.content)


def extract_zip(zip_bytes):
    with zipfile.ZipFile(zip_bytes) as zip_file:
        # # Extract all files from the ZIP, assuming single file for simplicity
        # for file_name in zip_file.namelist():
        #     with zip_file.open(file_name) as file:
        #         data = file.read()
        #         return data
        # Assumes there is only one XML file in the ZIP
        with zip_file.open(zip_file.namelist()[0]) as xml_file:
            xml_content = xml_file.read()
    return ET.fromstring(xml_content)


# Function to parse health-topic XML data
def parse_health_topic(element):
    # Extracts information and structures it for insertion
    also_called = [ac.text for ac in element.findall('also-called')]
    full_summary = element.find('full-summary').text if element.find('full-summary') is not None else None
    groups = [grp.text for grp in element.findall('group')]
    language_mapped_topic = element.find('language-mapped-topic').text if element.find(
        'language-mapped-topic') is not None else None
    mesh_heading = element.find('mesh-heading').text if element.find('mesh-heading') is not None else None
    other_language = element.find('other-language').text if element.find('other-language') is not None else None
    primary_institute = element.find('primary-institute').text if element.find(
        'primary-institute') is not None else None
    see_reference = element.find('see-reference').text if element.find('see-reference') is not None else None
    sites = [site.text for site in element.findall('site') if site.text.strip()]

    return (also_called, full_summary, groups, language_mapped_topic, mesh_heading,
            other_language, primary_institute, see_reference, sites)


# Function to insert parsed data into PostgreSQL
def insert_into_postgres(data, connection):
    with connection.cursor() as cursor:
        insert_query = """
        INSERT INTO health_topics (
            also_called, full_summary, groups, language_mapped_topic, mesh_heading, 
            other_language, primary_institute, see_reference, sites
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        cursor.execute(insert_query, data)
    connection.commit()


# Main function
def main():
    url = os.getenv("DATA_URL")
    # url = "https://medlineplus.gov/xml/mplus_topics_compressed_2024-10-31.zip"
    zip_data = download_file(url)
    extracted_data = extract_zip(zip_data)
    # Connect to the PostgreSQL database
    connection = psycopg2.connect(**db_config)
    # Iterate over each 'health-topic' element and insert into DB
    for health_topic in extracted_data.findall('health-topic'):
        parsed_data = parse_health_topic(health_topic)
        insert_into_postgres(parsed_data, connection)

    # Close database connection
    connection.close()


if __name__ == "__main__":
    main()
