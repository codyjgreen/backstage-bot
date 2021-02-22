import os
import logging
import ssl
import json
import pprint

# Import WebClient from Python SDK (github.com/slackapi/python-slack-sdk)
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = logging.getLogger("slack")

ssl._create_default_https_context = ssl._create_unverified_context

# WebClient insantiates a client that can call API methods
# When using Bolt, you can use either `app.client` or the `client` passed to listeners.
token=os.environ.get("SLACK_BOT_TOKEN")
if token == None:
    logger.error("Set SLACK_BOT_TOKEN")
    exit(-2)

client = WebClient(token=token)

# You probably want to use a database to store any user information ;)
users_store = {}

# Put users into the dict
def save_users(users_array):
    for user in users_array:
        # Key user info on their unique user ID
        user_id = user["id"]
        print(user['profile']['real_name'], user_id)
       
        # FIXME: No way to remove them from the user list using slack API?
        if "is_restricted" in user and user["is_restricted"]==True:
            print(user['profile']['real_name'], "is_restricted")
            continue
        
        if "is_bot" in user and user["is_bot"]==True:
            print(user['profile']['real_name'], "is_bot")
            continue

        if "deleted" in user and user["deleted"]==True:
            print(user['profile']['real_name'], "is_deleted")
            continue

        # Perhaps slackbot
        if user['updated'] == 0:
            print(user['profile']['real_name'], "is_slack_bot?")
            continue

        # Store the entire user object (you may not need all of the info)
        users_store[user_id] = user

'''
retrieve can be multiple calls
so we call it first, then collect results from users
'''

def get_user_ids():
    _retrieve_user_ids()
    return list(users_store.keys())  

def _retrieve_user_ids(cursor = None):
    try:
        # Call the users.list method using the WebClient
        # users.list requires the users:read scope
        result = client.users_list(cursor=cursor)
        pprint.pprint(result["response_metadata"])
        next_cursor = result['response_metadata']['next_cursor']
       
        save_users(result["members"])
        if 'next_cursor' in result['response_metadata']:
            next_cursor = result['response_metadata']['next_cursor']
            if next_cursor:
                print("Next cursor", next_cursor)
                # Call this recursively
                _retrieve_user_ids(next_cursor)

    except SlackApiError as e:
        logger.error("Error creating conversation: {}".format(e))


'''
Find the public channel or create one if not exist
'''
def get_backstage_channel_id(channel_name="backstage_story"):
    try:
        # search for channels first
        # FIXME: search channel id using name in slack API?
        result = client.conversations_list(exclude_archived=True, limit=1000)
        for channel in result['channels']:
            if channel['name'] == channel_name:
                return channel['id']
    
        # Perhaps, there is no channel, let's create
        result = client.conversations_create(
            # The name of the conversation
            name=channel_name
        )
        return result['channel']['id']
    except SlackApiError as e:
        logger.error("Error creating conversation: {}".format(e))

    return None
   
def get_realname(user_id):
    result = client.users_info(
        user=user_id
    )
    print(result)
    return result['user']['profile']['real_name']

def _send_channel_msg(channel_id, msg = "Hello!"):
    try:
        response = client.chat_postMessage(
            channel=channel_id,
            link_names=2,
            text=msg
        )
        print(response)
    except SlackApiError as e:
        logger.error("Error creating conversation: {}".format(e))

def send_pub_msg(msg, users_to_invite=None, channel_id=None):
    if not channel_id: # Allow overriding the channel id for debugging
        channel_id = get_backstage_channel_id()

    if channel_id == None:
        logger.error("cannot get the channel id!")
        return

    # Let's invite them if they are not in the room   
    if users_to_invite: 
        try:
            response = client.conversations_invite(
                channel=channel_id,
                users = users_to_invite
            )
            print(response)
        except SlackApiError as e:
            logger.error("Error inviting users to conversation: {}".format(e))

    _send_channel_msg(channel_id, msg)


def send_mim_msg(star1, star2, msg = "Hello!", channel_id=None):
    if not channel_id:
        response = client.conversations_open(users=[star1, star2])   
        if not response['ok']:
            logger.error("Cannot open mim: {}".format(response))
            return

        channel_id = response['channel']['id']
    
    _send_channel_msg(channel_id, msg)



if __name__ == '__main__':
    #open_mim_send_msg('U017Z0Y2P9P', 'U017FMWG9CJ')
    print(get_user_ids())
    r = get_backstage_channel_id()
    _send_channel_msg(r)