import csv
import datetime
import os
from zoomus import ZoomClient
from utils import *
from decouple import config
from ZoomClassStats.utils import *

"""
Flow:
-> find users in role 2 
    -> find meetings assigned to each 
        -> find the respective meeting ids
            -> report stats of each meeting: participants and registrants
"""

API_KEY = config('API_KEY')
API_SECRET = config('API_SECRET')

todayDate = datetime.date.today()
Hour = str(datetime.datetime.now())[11:13]
Minute = str(datetime.datetime.now())[14:16]
DIR_NAME = "./data/" + str(todayDate) + "-" + Hour + "-" + Minute

header = ["Meeting Name", "Meeting ID", "Meeting Location", "Meeting Grades", "Meeting Time", "Organizer",
          "Organizer Department", "Organizer Location", "Participant Name" , "Registration_email" ]

location = []

os.mkdir(DIR_NAME)
os.chdir(DIR_NAME)

# initialize the client
client = ZoomClient(API_KEY, API_SECRET)

for role in range(2):

    # look for users that are categorized under role_id '2' i.e. all the teacher
    # initial call to get the page counts
    user_init = json.loads(client.user.list(role_id=role + 1, page_size=300).content)

    user_page_count = int(user_init["page_count"])

    meeting_count = 0
    user_count = 0

    for user_page_number in range(user_page_count):
        # user list data on page -> page_number
        user_list = json.loads(
            client.user.list(role_id=role + 1, page_size=300, page_number=user_page_number + 1).content
        )

        print("user_list")
        print(user_list)

        # group_dict = get_groups(client)

        for user in user_list["users"]:
            user_count += 1

            useremail = user["email"]



            user_id = user["id"]
            user_obj = json.loads(client.user.get(id=user_id).content)

            """
             | Code to get group information
             | for each organizer
            \|/
            """

            # Uncomment if needed
            group_dict = get_groups(client)
            group_names = []
            if user.get("group_ids") is not None:
                user_groups = user["group_ids"]
                for group_id in user_groups:
                    if group_id in group_dict:
                        group_names.append(group_dict[group_id])

            else:
                group_names.append("No Groups Assigned")

            organizer_name = user_obj["first_name"] + " " + user_obj["last_name"]
            organizer_dept = ""

            organizer_loc = user_obj["location"]

            meeting_init = json.loads(client.meeting.list(user_id=user_id, page_number=1, type="past").content)

            print("meeting_init")
            print(meeting_init)

            meeting_page_count = int(meeting_init["page_count"])

            for meeting_page_number in range(meeting_page_count):
                meeting_obj = json.loads(
                    client.meeting.list(user_id=user_id, page_number=meeting_page_number + 1, type="past").content)
                meetings = meeting_obj["meetings"]

                print("meetings")
                print(meetings)

                if len(meetings) > 0:
                    for meeting in meetings:
                        meeting_count += 1

                        meeting_id = meeting["id"]
                        meeting_name1 = meeting["topic"]
                        meeting_name = meeting_name1 \
                            .replace("/", " ").replace("Aash-", "NotREC ").replace("AASH-", "NotREC ") \
                            .replace("Mosaic", "NotREC ").replace("Aash", "NotREC ") \
                            .replace("Aash ", "NotREC ").replace("AKHB", "NotREC ") \
                            .replace("AKYSB", "NotREC ").replace("AKSWB", "NotREC ").replace("AKEB", "NotREC ") \
                            .replace("Curriculum", "NotREC").replace("July", "NotREC").replace("My Meeting", "NotREC ") \
                            .replace("AASH ", "NotREC").replace("Sunday ", "NotREC").replace("Monday ", "NotREC") \
                            .replace("Tuesday ", "NotREC").replace("Wednesday ", "NotREC ").replace("Thursday ","NotREC ")\
                            .replace("Friday ", "NotREC ").replace("Saturday ", "NotREC ")


                        # print("\tMeeting: {}".format(meeting_name))
                        meeting_loc = ""
                        meeting_grades = ""

                        try:
                            meeting_info = meeting_name.split("-", 1)
                            meeting_loc = meeting_info[0]
                            meeting_grades = meeting_info[1]
                        except ValueError:
                            continue
                        except IndexError:
                            continue

                        meeting_time = ""
                        meeting_report = get_meeting_report(meeting_id, client)
                        if meeting_report.get("start_time") is not None:
                            meeting_time = parse_date_string(meeting_report["start_time"])

                            registrant_count = 0
                            registrant_obj = get_registrants(meeting_id, client)

                            print("registrant")
                            print(registrant_obj)

                            registrant_email_list = []
                            if registrant_obj.get("registrants") is not None:
                                registrants = registrant_obj["registrants"]
                                for registrant in registrants:
                                    registrant_count += 1
                                    registrant_email = registrant["email"]
                                    registrant_email_list.append(registrant_email)

                                # remove duplicates from the registrant list
                                registrant_email_list =  list(set(registrant_email_list))
                                print(registrant_email_list)

                            participant_count = 0
                            participant_obj = get_participants(meeting_id, client)
                            participant_list = []

                            if participant_obj.get("participants") is not None:
                                participants = participant_obj["participants"]
                                #print("participants")
                                #print(participants)
                                for participant in participants:
                                    participant_count += 1
                                    participant_name = participant["name"].replace("\r\n", "\n").replace('\u2605', '')\
                                        .replace('\U0001f47d', '').replace(" ❤️", "").replace(" 🐉🐍", " ").replace("🐉", "").replace("💎💚🌲🦚🕊", "")
                                    participant_list.append(participant_name)

                                # remove duplicates from the participants list
                                participant_list = list(set(participant_list))
                                print(participant_list)

                            section = []
                            section_iter = 0

                            # if len(registrant_email_list) < len(participant_list):
                            #     section_iter = len(registrant_email_list)
                            # else: section_iter = len(participant_list)
                            #
                            # for i in range(section_iter):
                            #     print(i)
                            #     section.append([meeting_name, meeting_id, meeting_loc, meeting_grades, meeting_time,
                            #                     organizer_name, organizer_dept, organizer_loc,
                            #                     participant_list[i], registrant_email_list[i]])
                            section_length = 0

                            if len(participant_list) <= len(registrant_email_list):
                                section_length = len(registrant_email_list)
                            else:
                                section_length = len(participant_list)

                            section = []

                            for i in range(section_length):
                                section.append([meeting_name, meeting_id, meeting_loc, meeting_grades, meeting_time,
                                                organizer_name, organizer_dept, organizer_loc, "", ""])

                            for i in range(len(registrant_email_list)):
                                section[i][8] = registrant_email_list[i]

                            for i in range(len(participant_list)):
                                section[i][9] = participant_list[i]

                            # print(registrant_list)
                            # print(participant_list)

                            print(section)

                            curr_csv_name = meeting_loc + '.csv'

                            if section and (meeting_loc in location):
                                # Write the CSV File
                                with open(curr_csv_name, 'a', newline='', encoding="utf-8") as report_file:
                                    writer = csv.writer(report_file)
                                    writer.writerows(section)
                                    print("Meeting Successfully Added!")

                            elif section and (meeting_loc not in location):
                                location.append(meeting_loc)
                                with open(curr_csv_name, 'w', newline='' , encoding="utf-8") as report_file:
                                    writer = csv.writer(report_file)
                                    writer.writerow(header)
                                    writer.writerows(section)
                                    print("Report File Configured for " + meeting_loc)

                        else:
                            pass
                            # print("\t\tNo Registrations found!\n")
                else:
                    pass
                    # print("\tNo Meetings Found\n")

