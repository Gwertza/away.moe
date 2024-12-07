import os
from datetime import datetime

import requests
import time
import subprocess
import pprint

from plyer import notification


class CourseTracker:
    """
    Tracks course availability for multiple courses and notifies on changes.
    """

    def __init__(self, friendly_names: dict = None):
        self.base_url = 'https://nubanner.neu.edu/StudentRegistrationSsb/ssb/'
        self.post_url = self.base_url + 'term/search'
        self.search_url = self.base_url + 'searchResults/searchResults'
        self.previous_states = {}
        self.friendly_names = {}
        if friendly_names is not None:
            self.friendly_names: dict = friendly_names

    def notify_windows(self, title, message):
        """
        Sends a notification using plyer.
        """
        notification.notify(
            title=title,
            message=message,
            app_name='Banner Scrape',
            timeout=10  # duration in seconds
        )

    def notify_mac(self, title, message):
        """ Sends a macOS notification using osascript. """

        subprocess.run(["osascript", "-e", f'display notification "{message}" with title "{title}"'])

    if os.name == 'nt':
        notify = notify_windows
    else:
        notify = notify_mac

    def fetch_courses(self, term, subject, course_number):
        """
        Fetches course data from the constructed URLs.
        """
        session = requests.Session()

        # POST request to set the term
        session.post(self.post_url, data={'term': term})

        # GET request to fetch course data
        payload = {
            'txt_subject': subject,
            'txt_courseNumber': course_number,
            'txt_term': term,
            'startDatepicker': '',
            'endDatepicker': '',
            'pageOffset': '0',
            'pageMaxSize': '50',
            'sortColumn': 'subjectDescription',
            'sortDirection': 'asc'
        }

        response = session.get(self.search_url, params=payload)
        if response.status_code != 200:
            print(f"Failed to fetch course data for {subject} {course_number} in term {term}.")
            return []

        data = response.json().get('data', [])
        if not isinstance(data, list):
            print(f"Unexpected data format for {subject} {course_number} in term {term}: {data}")
            return []

        return data

    def check_for_changes(self, course_key, courses):
        """
        Compares current course data with the previous state and notifies on changes.
        """
        if course_key not in self.previous_states:
            self.previous_states[course_key] = {}

        changes = []
        for course in courses:
            crn = course['courseReferenceNumber']
            available_seats = int(course['seatsAvailable'])
            previous_seats = self.previous_states[course_key].get(crn, {}).get('seatsAvailable', None)

            if previous_seats is None or available_seats != previous_seats:
                changes.append(
                    f"{course_key} - CRN {crn}: Seats changed from {previous_seats if previous_seats is not None else 'N/A'} to {available_seats}"
                )

            # Update the state
            self.previous_states[course_key][crn] = {
                'seatsAvailable': available_seats,
                'sequenceNumber': course['sequenceNumber']
            }

        return changes

    def monitor(self, term, courses, specific_section=None):
        """
        Monitors course availability for a list of courses.
        """

        def is_filtered(c):
            if specific_section is None:
                return True
            if c['courseNumber'] in specific_section:
                if c['courseReferenceNumber'] not in specific_section[c['courseNumber']]:
                    return False
            return True

        for subject, course_number in courses:
            course_key = f"{subject} {course_number} - {term}"
            current_c = self.fetch_courses(term, subject, course_number)
            current_courses = filter(lambda c: is_filtered(c), current_c)
            try:
                for course in current_courses:
                    print(self.friendly_names.get(course['courseNumber'], ""), course['courseReferenceNumber'],
                          course['courseNumber'], course['seatsAvailable'])
            except Exception as e:
                print("data not available")
                print(e)
            if not current_courses:
                print(f"No course data available for {course_key}.")
                continue

            changes = self.check_for_changes(course_key, current_courses)

            if changes:
                for change in changes:
                    self.notify("Course Update", change)
            # else:
            # self.notify("No Changes", f"No updates for {course_key}.")
        now = datetime.now()
        # Format the time as a string
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

        print(timestamp)
        print('________')
        return self.previous_states


def main():
    # List of courses (subject, course number) and the term
    courses = [("CS", "3800"), ("CS", "4410")]  # Add more courses as needed
    specific_section: dict[str, tuple[str]] = {"3302": (
        "31336", "32575", "31327", "31328", "31332", "32576", "31862", "32103", "33034", "33664", "33729", "33825",
        "31334",
        "33459", "35376", "32883"),
        "3800": ("30303",)}
    term = "202530"  # Spring 2025 term code
    friendly_names = {"4530": "Software Engineering",
                      "4100": "AI",
                      "3800": "Theory of Comp",
                      "3302": "Advanced Writing",
                      "4410": "Compilers",
                      "4610": "Robots"}
    tracker = CourseTracker(friendly_names)
    tracker.notify("Started Monitoring",
                   f"Monitoring courses: {', '.join([f'{s} {c}' for s, c in courses])} for term {term}.")

    while True:
        tracker.monitor(term, courses, specific_section)
        time.sleep(60)  # Check every 5 minutes


if __name__ == '__main__':
    main()
