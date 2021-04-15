import os
import logging
import ssl
import json
import pprint

# Import WebClient from Python SDK (github.com/slackapi/python-slack-sdk)
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = logging.getLogger("slack")
BACKSTAGE_CHANNEL_NAME = "all-backstage-story"

ssl._create_default_https_context = ssl._create_unverified_context

# WebClient insantiates a client that can call API methods
# When using Bolt, you can use either `app.client` or the `client` passed to listeners.
token=os.environ.get("SLACK_BOT_TOKEN")

if not token:
    logger.error("Set SLACK_BOT_TOKEN first")
    exit(-2)

client = WebClient(token=token)


'''
retrieve can be multiple calls
so we call it first, then collect results from users
'''
users_store = []
def get_user_ids(channel_name=BACKSTAGE_CHANNEL_NAME):
    channel = get_backstage_channel_id()
    _retrieve_user_ids_in_channel(channel)
    return users_store
    

def _retrieve_user_ids_in_channel(channel, cursor = None):
    global users_store

    try:
        # Call the users.list method using the WebClient
        # users.list requires the users:read scope
        result = client.conversations_members(channel=channel, cursor=cursor)
        pprint.pprint(result["response_metadata"])
        next_cursor = result['response_metadata']['next_cursor']
       
        for member in result["members"]:
            if not is_bot(member):
                users_store.append(member)
                
        if 'next_cursor' in result['response_metadata']:
            next_cursor = result['response_metadata']['next_cursor']
            if next_cursor:
                print("Next cursor", next_cursor)
                # Call this recursively
                _retrieve_user_ids_in_channel(channel, cursor=next_cursor)

    except SlackApiError as e:
        logger.error("Error getting members: {}".format(e))


'''
Find the public channel or create one if not exist
'''
def get_backstage_channel_id(channel_name=BACKSTAGE_CHANNEL_NAME):
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

def is_bot(user_id):
    result = client.users_info(
        user=user_id
    )
    return result['user']['is_bot']


def get_realname(user_id):
    result = client.users_info(
        user=user_id
    )
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
   ids = get_user_ids()
   for i, id in enumerate(ids):
       print(i, id, get_realname(id))

    #r = get_backstage_channel_id()
    #_send_channel_msg(r)
