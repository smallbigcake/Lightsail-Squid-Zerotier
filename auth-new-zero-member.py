#!/usr/bin/env python3
import time

import requests
import json

HOST = 'https://api.zerotier.com'
API_VERSION = '/api/v1'
NETWORK_ID = ''
GET_MEMBERS_URL = f'{HOST}{API_VERSION}/network/{NETWORK_ID}/member'
MODIFY_MEMBERS_URL = f'{HOST}{API_VERSION}/network/{NETWORK_ID}/member/%member_id%'
DELETE_MEMBERS_URL = f'{HOST}{API_VERSION}/network/{NETWORK_ID}/member/%member_id%'
LIGHTSAIL_NAME = 'Debian-Squid-IPv4'
MS_IN_SECOND = 1000
TIME_WAIT_ONLINE = 60
OFFLINE_THRESHOLD = 60 * 60 * 8
LIGHTSAIL_INTERNAL_IP = ''

HEADERS = {
    'Authorization': 'token '
}


def main():

    while True:
        members = get_members()
        # print(members)
        old_node_ids = get_old_lightsail_node_id(members)
        new_node_id = get_new_lightsail_node_id(members)
        delete_old_lightsail(old_node_ids)
        if new_node_id:
            print(f'Found New node id: {new_node_id}')
            auth_new_lightsail(new_node_id)
            break
        else:
            print(f'No new node found. Retrying in {TIME_WAIT_ONLINE} seconds')
            time.sleep(TIME_WAIT_ONLINE)

    return


def get_members():

    response = requests.get(GET_MEMBERS_URL, headers=HEADERS)
    return json.loads(response.text)


def get_new_lightsail_node_id(members):

    for each_member in members:
        if not each_member['config']['authorized']:
            return each_member['nodeId']


def get_old_lightsail_node_id(members):

    old_ids = []
    for each_member in members:
        if each_member['config']['authorized'] \
                and LIGHTSAIL_INTERNAL_IP in each_member['config']['ipAssignments'] \
                and each_member['name'] == LIGHTSAIL_NAME \
                and time.time() * MS_IN_SECOND - each_member['lastSeen'] > OFFLINE_THRESHOLD:
            old_ids.append(each_member['nodeId'])
    return old_ids


def delete_old_lightsail(member_id):
    for each_node_id in member_id:
        print(f'Found old node id: {each_node_id}. Deleting.')
        response = requests.delete(DELETE_MEMBERS_URL.replace('%member_id%', each_node_id), headers=HEADERS)
        if response.status_code == 200:
            print('Delete successful.')
        else:
            print(f'Delete failed.\n Code: {response.status_code}, message: {response.text}')


def auth_new_lightsail(member_id):
    data = {
        'name': LIGHTSAIL_NAME,
        # 'hidden': False,
        # 'description': '',

        'config': {
            'ipAssignments': [LIGHTSAIL_INTERNAL_IP],
            'authorized': True,
            # 'activeBridge': False,
            # 'noAutoAssignIps': False,
            # 'capabilities': [
            #     0
            # ]
        }
    }
    print(f'Adding new lightsail node: {member_id}')
    response = requests.post(MODIFY_MEMBERS_URL.replace('%member_id%', member_id), headers=HEADERS, json=data)

    if response.status_code == 200:
        print('Add successful.')
    else:
        print(f'Add failed.\n Code: {response.status_code}, message: {response.text}')


if __name__ == '__main__':
    main()
