import csv
import datetime
from zoomus import ZoomClient
from utils import *

"""
Flow:
-> find users in role 2 
    -> find meetings assigned to each 
        -> find the respective meeting ids
            -> report stats of each meeting: participants and registrants
"""

API_KEY = "FDzxXrLwR9WGePxqqYbooA"
API_SECRET = "X7wEDBNtG68L6P1aAxLCNhKERmLIGTCoPnwo"

todayDate = datetime.date.today()

CSV_FILE_NAME = str(todayDate) + ".csv"

header = ["Meeting Name", "Meeting ID", "Meeting Location", "Meeting Grades", "Meeting Time", "Organizer",
          "Organizer Department", "Organizer Location", "Participant Name"]

with open(CSV_FILE_NAME, 'wb') as report_file:
    writer = csv.writer(report_file)
    writer.writerow(header)
    print("Report File Configured!")

# initialize the client
client = ZoomClient(API_KEY, API_SECRET)

for role in range(2):
    print(role)
    # look for users that are categorized under role_id '2' i.e. all the teacher
    # initial call to get the page counts
    user_init = json.loads(client.user.list(role_id=role + 1, page_size=300).content)

    user_page_count = int(user_init["page_count"])

    meeting_count = 0
    user_count = 0

    for user_page_number in range(user_page_count):
        # user list data on page -> page_number
        user_list = json.loads(
            client.user.list(role_id=role + 1, page_size=300, page_number=user_page_number + 1).content)

        # group_dict = get_groups(client)

        for user in user_list["users"]:
            user_count += 1

            user_id = user["id"]
            user_obj = json.loads(client.user.get(id=user_id).content)

            """
             | Code to get group information
             | for each organizer
            \|/
            """
            # group_names = []
            # if user.get("group_ids") is not None:
            #     user_groups = user["group_ids"]
            #     for group_id in user_groups:
            #         if group_id in group_dict:
            #             group_names.append(group_dict[group_id])
            #
            # else:
            #     group_names.append("No Groups Assigned")

            organizer_name = user_obj["first_name"] + " " + user_obj["last_name"]
            # if user_obj.get("dept") is not None:
            organizer_dept = ""
            # else:
            #     organizer_dept = user_obj["dept"]
            organizer_loc = user_obj["location"]

            # print("Organizer: {}".format(organizer_name))

            meeting_init = json.loads(client.meeting.list(user_id=user_id).content)
            meeting_page_count = int(meeting_init["page_count"])
            # meetings = meeting_obj["meetings"]
            # print("\t\t" + str(meeting_page_count))

            for meeting_page_number in range(meeting_page_count):
                meeting_obj = json.loads(
                    client.meeting.list(user_id=user_id, page_number=meeting_page_number + 1, type="past").content)
                meetings = meeting_obj["meetings"]

                if len(meetings) > 0:
                    for meeting in meetings:
                        meeting_count += 1

                        meeting_id = meeting["id"]
                        meeting_name = meeting["topic"]

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
                            meeting_time = parse_date(meeting_report["start_time"])

                        # registrant_count = 0
                        registrant_obj = get_registrants(meeting_id, client)

                        # print("\t\t---- Registrants ----")

                        # if registrant_obj.get("registrants") is None:
                        #     print("\t\tNo Registrations found!\n")
                        #     break

                        if registrant_obj.get("registrants") is not None:
                            registrants = registrant_obj["registrants"]

                            # registrant_list = []
                            participant_list = []

                            # for registrant in registrants:
                            #     registrant_count += 1
                            #     # print(registrant)
                            #
                            #     registrant_first_name = registrant["first_name"].encode('utf-8')
                            #     registrant_last_name = ""
                            #     if registrant.get("last_name") is not None:
                            #         registrant_last_name = registrant["last_name"].encode('utf-8')
                            #     registrant_name = registrant_first_name + registrant_last_name
                            #
                            #     registrant_list.append(registrant_name)

                                # print("\t\t" + registrant_name)
                                # output_file.writelines('\t' + participant['name'])

                            # remove duplicates from the registrant list
                            # registrant_list = list(set(registrant_list))

                            # print("\t\t-> Registrant Count: {}\n".format(registrant_count))

                            participant_count = 0
                            participant_obj = get_participants(meeting_id, client)

                            # print("\t\t---- Participants ----")

                            # if participant_obj.get("participants") is None:
                            #     print("\t\tMeeting hasn't taken place yet!\n")

                            # else:
                            if participant_obj.get("participants") is not None:
                                participants = participant_obj["participants"]
                                # print(participants)

                                for participant in participants:
                                    participant_count += 1
                                    # print("\t\t" + participant["name"])
                                    participant_name = participant["name"].encode('utf-8')
                                    participant_list.append(participant_name)
                                    # output_file.writelines('\t' + participant['name'])

                                # remove duplicates from the registrant list
                                participant_list = list(set(participant_list))

                            # section_length = 0
                            #
                            # if len(participant_list) <= len(registrant_list):
                            #     section_length = len(registrant_list)
                            # else:
                            #     section_length = len(participant_list)
                            #
                            section = []

                            for i in range(len(participant_list)):
                                section.append([meeting_name, meeting_id, meeting_loc, meeting_grades, meeting_time,
                                                organizer_name, organizer_dept, organizer_loc, participant_list[i]])

                            # for i in range(len(registrant_list)):
                            #     section[i][8] = registrant_list[i]
                            #
                            # for i in range(len(participant_list)):
                            #     section[i][9] = participant_list[i]
                            #
                            # for i in range(len(ipaddress_list)):
                            #     section[i][10] = ipaddress_list[i]
                            #
                            # for i in range(len(geolocation_list)):
                            #     section[i][11] = geolocation_list[i]

                            # print(registrant_list)
                            # print(participant_list)
                            print(section)

                            # Write the CSV File
                            with open(CSV_FILE_NAME, 'ab') as report_file:
                                writer = csv.writer(report_file)
                                writer.writerows(section)
                                print("Meeting Successfully Added!")

                            # csv_rows += section
                            #
                            # print(csv_rows)

                            # print("\t\t-> Participant Count: {}\n".format(participant_count))

                        else:
                            pass
                            # print("\t\tNo Registrations found!\n")

                else:
                    pass
                    # print("\tNo Meetings Found\n")

# print("---- End Report ----")
# print("Meeting Count: {}".format(meeting_count))
# print("User Count: {}".format(user_count))
