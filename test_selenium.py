from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pytest
import time
import sqlite3
from itertools import product
from datetime import datetime

search_terms = ["Blood on the Clocktower", "Duck Watching", "notInList", "𐏂𐎤𐎽𐏂"]
start_dates = ["14-02-2025", "14-03-2025", "14-04-2025", "hello", "2025-04-14"]
end_dates = ["14-02-2025", "14-03-2025", "14-04-2025", "hello", "2025-04-14"]

def is_valid_time(time_str):
    try:
        datetime.strptime(time_str, "%H:%M").time()
        return True
    except ValueError:
        return False
    
def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, "%d-%m-%Y").date()
        return True
    except ValueError:
        return False

def is_valid_combination(search, start_date, end_date):
    # If the search term is not in the valid list, the combination is invalid
    if search not in ["Blood on the Clocktower", "Duck Watching"]:
        return False
    

    # If the dates or times contain non-numeric values (like "hello"), the combination is invalid
    if "hello" in [start_date, end_date]:
        return False
    
    if not is_valid_date(start_date) or not is_valid_date(end_date):
        return False

    # If the end date is before the start date, it's invalid
    if datetime.strptime(start_date, "%d-%m-%Y").date() > datetime.strptime(end_date, "%d-%m-%Y").date():
        return False
    
    if search == "Blood on the Clocktower" and (datetime.strptime(start_date, "%d-%m-%Y").date() > datetime.strptime("2025-03-14", "%Y-%m-%d").date()) or datetime.strptime(end_date, "%d-%m-%Y").date() < datetime.strptime("2025-03-21", "%Y-%m-%d").date():
        return False
    
    if search == "Duck Watching" and (datetime.strptime(start_date, "%d-%m-%Y").date() > datetime.strptime("2025-04-02", "%Y-%m-%d").date()) or datetime.strptime(end_date, "%d-%m-%Y").date() < datetime.strptime("2025-04-02", "%Y-%m-%d").date():
        return False
    # Otherwise, it's a valid combination
    return True

# Generate all possible combinations of test cases
all_combinations = list(product(search_terms, start_dates, end_dates ))

# Assign validity labels to each combination
test_cases = [(s, sd, ed, is_valid_combination(s, sd, ed)) for (s, sd, ed) in all_combinations]


@pytest.fixture
def driver():
    """Set up WebDriver instance for each test."""
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)
    driver.get("http://127.0.0.1:5000/")  
    time.sleep(2)

    yield driver  # Provide the WebDriver instance

    driver.quit()  # Close WebDriver after each test

@pytest.mark.parametrize("element", ["navLogo", "everythingContainer", "contentContainer", "leftContainer", "searchBox", "filterContainer", "startDate", "endDate", "startTime", "endTime", "subscribed", "dividingLine", "eventsContainer", "userContainer"])
def test_for_elements(driver, element):
    driver.get("http://127.0.0.1:5000/")
    time.sleep(2)  # Allow page to load

    tested_element = driver.find_element(By.ID, element)
    assert tested_element is not None, f"{element} list not found on the page."

@pytest.mark.parametrize("element", ["profileContainer"])
def test_for_classes(driver, element):
    driver.get("http://127.0.0.1:5000/")
    time.sleep(2)  # Allow page to load

    tested_element = driver.find_element(By.CLASS_NAME, element)
    assert tested_element is not None, f"{element} list not found on the page."


@pytest.mark.parametrize("search, start_date, end_date, expected_result", test_cases)
def test_filters(driver, search, start_date, end_date, expected_result):
    driver.get("http://127.0.0.1:5000/")
    time.sleep(2)  # Allow page to load
    boxes = ["subscribed", "favorited", "onCampus", "societyEvent", "ticketedEvent"]

    driver.find_element(By.ID, "searchBox").send_keys(search)
    
    driver.find_element(By.ID, "startDate").send_keys(start_date)
    
    driver.find_element(By.ID, "endDate").send_keys(end_date)
    
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    


    time.sleep(2)  # Wait for the search results to load


    search_list = driver.find_element(By.ID, "eventsContainer") #check if search results exist
    assert search_list is not None, "Search results not found."

    if expected_result == True:
        # Locate all events that match the search term
        event_xpath = f'//div[@class="profileContainer"]//div[@class="eventText"]/h1[contains(text(), "{search}")]'
        event_elements = driver.find_elements(By.XPATH, event_xpath)

        assert event_elements, f"No searched events found for '{search}'"

        for event in event_elements:
            try:

                event_date_text = event.find_element(By.XPATH, '//div[@class="profileContainer"]//div[@class="eventText"]/h2[@id="eventDate"]').text.strip()

                # Convert extracted values into datetime objects
                event_date = datetime.strptime(event_date_text[:10], "%Y-%m-%d").date()

                start_date_obj = datetime.strptime(start_date, "%d-%m-%Y").date()
                end_date_obj = datetime.strptime(end_date, "%d-%m-%Y").date()

                # Ensure extracted values are valid before checking ranges
                assert event_date is not None, f"Invalid event date format: {event_date_text}"
                # assert event_time is not None, f"Invalid event time format: {event_time_text}"

                # Validate the event falls within the given filters
                assert start_date_obj <= event_date <= end_date_obj, f"Event date {event_date} is out of range ({start_date} - {end_date})"
                # assert start_time_obj <= event_time <= end_time_obj, f"Event time {event_time} is out of range ({start_time} - {end_time})"

            except Exception as e:
                assert False, f"Error processing event data: {e}"

@pytest.mark.parametrize("element", ["formPage", "formContainer", "loginForm", "registerLink"])
def test_for_classes_login_page(driver, element):
    driver.get("http://127.0.0.1:5000/login")
    time.sleep(2)  # Allow page to load

    tested_element = driver.find_element(By.CLASS_NAME, element)
    assert tested_element is not None, f"{element} list not found on the page."
    
@pytest.mark.parametrize("username, password, result",[
    ("test123", "123", True),
    ("test123", "failPassword", False),
    ("test123", "𐏂𐎤𐎽𐏂", False),
    ("𐏂𐎤𐎽𐏂", "123", False),
    ("test123", "", False),
    ("","123", False),
    ("𐏂𐎤𐎽𐏂", "𐏂𐎤𐎽𐏂", False),
    ("", "", False)
])
def test_login(driver, username, password, result):
    driver.get("http://127.0.0.1:5000/login")
    time.sleep(2)  # Allow page to load
    
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.XPATH, '//input[@type="submit"]').click()
    
    time.sleep(2)  # Allow page to load
    
    if result == True:
        assert driver.current_url == "http://127.0.0.1:5000/", "Failed to login"
    else:
        assert driver.current_url == "http://127.0.0.1:5000/login", "Mistakenly logged in"
        


def test_login(driver):
    driver.get("http://127.0.0.1:5000")
    time.sleep(2)  # Allow page to load

    driver.find_element(By.NAME, "username").send_keys("' OR '1'='1' -- ")
    driver.find_element(By.NAME, "password").send_keys("abc")
    driver.find_element(By.XPATH, '//input[@type="submit"]').click()
    
    time.sleep(2)  # Allow response to load

    assert driver.current_url == "http://127.0.0.1:5000/login", "Mistakenly logged in"

