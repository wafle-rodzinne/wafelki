

from difflib import SequenceMatcher

def prepareAlphaList():
    alist = {'a':[],'b':[],'c':[],
             'd':[],'e':[],'f':[],
             'g':[],'h':[],'i':[],
             'j':[],'k':[],'l':[],
             'm':[],'n':[],'o':[],
             'p':[],'q':[],'r':[],
             's':[],'t':[],'u':[],
             'v':[],'w':[],'x':[],
             'y':[],'z':[]}
    return alist

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def game(db, streamer_name, answers, mode):
    alpha_list = getAlphabeticalList(db, streamer_name, mode)
    results = {}
    top1 = {}
    max_points = 26
    from string import ascii_lowercase

    for i, letter in enumerate(ascii_lowercase):
        answer = answers[i]
        answer_position  = 997
        top_letter_count = len(alpha_list[letter])

        if len(alpha_list[letter]) > 0:
            top1.update({letter : [alpha_list[letter][0]['user'], alpha_list[letter][0]['val']]})
        else:
            results.update({letter : 'nouser'})
            top1.update({letter : ['-', 0]})
            continue

        if not answer:
            results.update({letter : 'noanswer'})
            continue

        for rank, top_letter_user in enumerate(alpha_list[letter]):
            if similar(answer, top_letter_user['user']) >= 0.75:
                answer_position = rank
                break
        category, max_points = getAnswerCategory(answer_position, top_letter_count, max_points)
        
        results.update({letter : category})

    return [results, top1, max_points]


def getAlphabeticalList(db, streamer_name, column):
    alphabetical_list = prepareAlphaList()
    top_entries = db.execute(
        f'SELECT chatter_name, {column} FROM chatters, channels_chatters, channels \
         WHERE channels.streamer == (?) \
         AND channels.channel_id == channels_chatters.channel_id \
         AND channels_chatters.chatter_id == chatters.chatter_id \
         ORDER BY {column} DESC',
        (streamer_name,),
    ).fetchall()
    for entry in top_entries:
        user = entry[0]
        val  = entry[1]
        first_letter = user[0].lower()
        from string import ascii_lowercase
        if not first_letter in ascii_lowercase:
            continue
        alphabetical_list[first_letter].append({'user':user, 'val':val})
    return alphabetical_list

def getAnswerCategory(answer_position, top_letter_count, max_points):
    if answer_position  == 0:                               # exact
        return ['exact', max_points]
    elif answer_position < 5:                               # close
        return ['close', max_points]
    elif answer_position == 997 and top_letter_count >= 5: # far
        return ['far', max_points]
    elif top_letter_count == 0:                             # nouser
        max_points -= 1
        return ['nouser', max_points]
    elif answer_position == 997 and top_letter_count < 5:  # unknown
        return ['unknown', max_points]
    else:
        max_points -= 1
        return ['unknown', max_points]
