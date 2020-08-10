import json


def get_participants(meet_id, client_pointer, page_size=300):
    resp_obj = client_pointer.get_request(
        "/report/meetings/{}/participants?type=past&page_size={}".format(meet_id, str(page_size)))
    return json.loads(resp_obj.content)


def get_ipaddress(meet_id, client_pointer, page_size=300):
    # type: (object, object, object) -> object
    resp_obj = client_pointer.get_request(
        "/metrics/meetings/{}/participants/qos?type=past&page_size={}".format(meet_id, str(page_size)))
    return json.loads(resp_obj.content)


def get_registrants(meet_id, client_pointer, page_size=300):
    resp_obj = client_pointer.get_request("/meetings/{}/registrants?page_size={}".format(meet_id, str(page_size)))
    return json.loads(resp_obj.content)


def get_groups(client_pointer, page_size=300):
    resp_obj = client_pointer.get_request("/groups")
    group_list = json.loads(resp_obj.content)["groups"]
    group_dict = {}

    for group in group_list:
        group_dict[group["id"]] = group["name"]

    return group_dict


def parse_date_string(date_string):
    date_time = date_string.split("T")
    date_all = date_time[0].split("-")
    date_format = date_all[1] + "/" + date_all[2] + "/" + date_all[0]
    time = date_time[1][:-4]

    return date_format + " " + time


def parse_date_int(date_string):
    date_time = date_string.split("T")
    time = date_time[1][:-1].split(":")
    return time[0] * 3600 + time[1] * 60 + time[2]


def get_meeting_report(meet_id, client_pointer, page_size=300):
    resp_obj = client_pointer.get_request("//report/meetings/{}".format(meet_id))
    return json.loads(resp_obj.content)
