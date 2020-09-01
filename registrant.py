import csv
import datetime
import json
from zoomus import ZoomClient
from decouple import config
from ZoomClassStats.utils import *

"""
Flow:
-> find users with "vre." in email
    -> find meetings assigned to each 
        -> find the respective meeting ids
            -> count registrants for each
"""

API_KEY = config('API_KEY')
API_SECRET = config('API_SECRET')

todayDate = datetime.date.today()

CSV_FILE_NAME = "./data/REG-COUNT-" + str(todayDate) + ".csv"

ROLE = 2

EMAIL_IDENTIFIER = "vre."
EMAIL_IDENTIFIER1 = ".org"
EMAIL_IDENTIFIER2 = "zoom"
STEP_LITERAL = "STEP Teachers"

header = ["User Name", "Group Name", "Meeting Name", "Registrant Count"]

with open(CSV_FILE_NAME, 'w', newline='') as report_file:
    writer = csv.writer(report_file)
    writer.writerow(header)
    print("Report File Configured! ")

# initialize the client
client = ZoomClient(API_KEY, API_SECRET)

# look for users that are categorized under role_id '2' i.e. all the teacher
# initial call to get the page counts
user_init = json.loads(client.user.list(role_id=ROLE, page_size=300).content)

user_page_count = int(user_init["page_count"])

meeting_count = 0

for user_page_number in range(user_page_count):
    # user list data on page -> page_number
    user_list = json.loads(
        client.user.list(role_id=ROLE, page_size=300, page_number=user_page_number + 1).content
    )

    for user in user_list["users"]:

        user_email = user["email"]

        reg_count_tot = 0

        group_name = ""

        if user.get("group_ids") is not None:
            group_obj = get_group(user["group_ids"][0], client)
            group_name = group_obj["name"]

        if (EMAIL_IDENTIFIER in user_email) or (group_name == STEP_LITERAL) or (
                EMAIL_IDENTIFIER1 in user_email) and not (EMAIL_IDENTIFIER2 in user_email):

            user_id = user["id"]

            meeting_init = json.loads(client.meeting.list(user_id=user_id, page_number=1, type="past").content)
            meeting_page_count = int(meeting_init["page_count"])

            for meeting_page_number in range(meeting_page_count):
                meeting_obj = json.loads(
                    client.meeting.list(user_id=user_id, page_number=meeting_page_number + 1, type="past").content)
                meetings = meeting_obj["meetings"]

                for meeting in meetings:
                    # meeting_count += 1

                    meeting_id = meeting["id"]
                    meeting_name = meeting["topic"]

                    registrant_obj = get_registrants(meeting_id, client)
                    print(meeting)

                    if registrant_obj.get("registrants") is not None:
                        registrants = registrant_obj["registrants"]

                        registrant_list = []
                        registrant_count = 0

                        for registrant in registrants:
                            registrant_count += 1
                            reg_count_tot += 1
                            # print(registrant)

                            registrant_first_name = registrant["first_name"]
                            registrant_last_name = ""
                            if registrant.get("last_name") is not None:
                                registrant_last_name = registrant["last_name"]
                            registrant_name = registrant_first_name + registrant_last_name
                            registrant_list.append(registrant_first_name + " " + registrant_last_name)

                        # remove duplicates from the registrant list
                        registrant_list = list(set(registrant_list))

                        section = [user_email, group_name, meeting_name, registrant_count]

                        # Write the CSV File
                        with open(CSV_FILE_NAME, 'a', newline='') as report_file:
                            writer = csv.writer(report_file)
                            writer.writerow(section)
                            print("Meeting Successfully Added!")

                    else:
                        pass
                        # print("\t\tNo Registrations found!\n")

            print("\n" + user_email + " | " + group_name + " | " + str(registrant_count))

            section = [user_email, group_name, "TOTAL=", reg_count_tot]

            # Write the CSV File
            with open(CSV_FILE_NAME, 'a', newline='') as report_file:
                writer = csv.writer(report_file)
                writer.writerow(section)
                print("Meeting Successfully Added!")
