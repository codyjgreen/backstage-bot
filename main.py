
from slack import get_user_ids, send_mim_msg, send_pub_msg
from db import db_init, db_add_stars, db_get_matches, db_close

msg_template = '''
<@{}>, <@{}>님을 백스테이지로 초대합니다! :sunglasses::sparkles:\n\n
한주를 시작하기 전 가볍게 함께 티타임을 가지시는 건 어떨까요?\n
주말동안 있었던 일, 흥미로운 소식, 나누고 싶은 이야기 등으로 함께 편안한 시간 보내시며,
이번주도 모두 모두 화이팅할 수 있는 기운을 나눠주세요 :female_superhero::male_superhero::rocket:\n\n
멋진 시간 보내신 사진등을 #backstage_story 에 올려주세요.\n
'''

pub_msg_template = '''
이번주에도 <@{}>, <@{}>님등 총 {} 쌍을 백스테이지로 초대했습니다. 한주를 시작하기 전 가볍게 티타임을 가져주시고, 
멋진 시간 보내신 사진과 스토리 이 채널에 많이 올려주세요
'''

if __name__ == '__main__':
    # Get all users from slack
    stars = get_user_ids()
    if len(stars) == 0:
        print("Hmm. No users to match")
        exit(-1)

    # Open local dbfile and add users
    db_init()
    db_add_stars(stars)

    pairs = 0
    # get matches based on the previous meetings
    for star1, star2 in db_get_matches():
        msg = msg_template.format(star1, star2)

        # DEBUG
        # star1 = 'U018RFQP6CX' # Yura
        # star2 = 'U017FMWG9CJ' # Sung
        # Open mim and send a message
        send_mim_msg(star1, star2, msg=msg)
        pairs = pairs + 1
        # break ## Send only one for testing

    # Send public message
    pub_msg = pub_msg_template.format(star1, star2, pairs)
    send_pub_msg(pub_msg, [star1, star2])

    db_close()

