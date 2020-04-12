import json
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

# initialize the client
client = ZoomClient(API_KEY, API_SECRET)

# look for users that are categorized under role_id '2' i.e. all the teacher
# initial call to get the page counts
user_init = json.loads(client.user.list(role_id=2, page_size=300).content)

user_page_count = int(user_init["page_count"])

meeting_count = 0
user_count = 0

for user_page_number in range(user_page_count):
    # user list data on page -> page_number
    user_list = json.loads(client.user.list(role_id=2, page_size=300, page_number=user_page_number+1).content)

    group_dict = get_groups(client)

    for user in user_list["users"]:
        user_count += 1
        user_id = user["id"]

        group_names = []
        if user.get("group_ids") is not None:
            user_groups = user["group_ids"]
            for group_id in user_groups:
                if group_id in group_dict:
                    group_names.append(group_dict[group_id])

        else:
            group_names.append("No Groups Assigned")

        print("{}: {} {}. Groups: {}".format(user_id, user["first_name"], user["last_name"], ", ".join(group_names)))

        meeting_init = json.loads(client.meeting.list(user_id=user_id).content)
        meeting_page_count = int(meeting_init["page_count"])
        # meetings = meeting_obj["meetings"]
        print("\t\t" + str(meeting_page_count))

        for meeting_page_number in range(meeting_page_count):
            meeting_obj = json.loads(client.meeting.list(user_id=user_id, page_number=meeting_page_number+1).content)
            meetings = meeting_obj["meetings"]

            if len(meetings) > 0:
                for meeting in meetings:
                    meeting_count += 1
                    meeting_id = str(meeting["id"])
                    print("\t{}: {}".format(str(meeting["id"]), meeting["topic"]))

                    participant_count = 0
                    participant_obj = get_participants(meeting_id, client)

                    print("\t\t---- Participants ----")

                    if participant_obj.get("participants") is None:
                        print("\t\tMeeting hasn't taken place yet!\n")

                    else:
                        participants = participant_obj["participants"]
                        # print(participants)

                        for participant in participants:
                            participant_count += 1
                            print("\t\t" + participant["name"])
                            # output_file.writelines('\t' + participant['name'])

                        print("\t\t-> Participant Count: {}\n".format(participant_count))

                    registrant_count = 0
                    registrant_obj = get_registrants(meeting_id, client)

                    print("\t\t---- Registrants ----")

                    if registrant_obj.get("registrants") is None:
                        print("\t\tNo Registrations found!\n")

                    else:
                        registrants = registrant_obj["registrants"]

                        for registrant in registrants:
                            registrant_count += 1
                            # print(registrant)
                            print("\t\t" + registrant["first_name"])
                            # output_file.writelines('\t' + participant['name'])

                        print("\t\t-> Registrant Count: {}\n".format(registrant_count))

            else:
                print("\tNo Meetings Found\n")

print("---- End Report ----")
print("Meeting Count: {}".format(meeting_count))
print("User Count: {}".format(user_count))
