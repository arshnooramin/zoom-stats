import json


def get_participants(meet_id, client_pointer, page_size=300):
    resp_obj = client_pointer.get_request(
        "/report/meetings/{}/participants?page_size={}".format(meet_id, str(page_size)))
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
