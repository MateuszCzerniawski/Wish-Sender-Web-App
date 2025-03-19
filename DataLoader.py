import csv
import os


def load_users():
    all_users = dict()
    with open('data/users.csv', 'r') as file:
        for line in csv.reader(file, delimiter=';'):
            if line.__len__() == 2:
                all_users[line[0]] = line[1]
    print(f'{all_users.__len__()} loaded')
    return all_users


def load_wish_tweaks():
    tweaks = dict()
    counter = 0
    with open('data/wishes/tweaks.csv', 'r') as file:
        for line in csv.reader(file, delimiter=';'):
            if not tweaks.__contains__(line[0]):
                tweaks[line[0]] = dict()
            wish = list()
            for i in range(2, line.__len__()):
                wish.append(str(line[i]))
            tweaks[line[0]][line[1]] = wish
            counter += 1
    print(f'{counter} tweaks detected')
    return tweaks


def load_wishes():
    wish_dir = 'data/wishes'
    all_wishes = dict()
    counter = 0
    for current_dir in os.listdir(wish_dir):
        if os.path.isdir(wish_dir + "/" + current_dir):
            all_wishes[current_dir] = dict()
            tmp = wish_dir + "/" + current_dir
            for name in os.listdir(tmp):
                with open(tmp + "/" + name, 'r', encoding='utf-8') as file:
                    all_wishes[current_dir][name] = file.read()
                counter += 1
    print(f'{counter} wishes loaded')
    return all_wishes


def load_prefixes():
    all_prefixes = dict()
    counter = 0
    with open('data/wishes/prefixes.csv', 'r') as file:
        for line in csv.reader(file, delimiter=';'):
            if line.__len__() == 2:
                all_prefixes[line[0]] = line[1]
                counter += 1
    print(f'{counter} prefixes loaded')
    return all_prefixes


def save_user(username, password):
    with open('data/users.csv', 'a') as file:
        file.write("\n" + username + ";" + password)


def load_discord_bot_config():
    discord_configurations = dict()
    with open('data/discord_bot.txt', 'r') as file:
        discord_configurations['invite'] = file.readline()[:-1]
        discord_configurations['token'] = file.readline()[:-1]
        discord_configurations['perm_int'] = file.readline()
    return discord_configurations


def load_auto_sends():
    auto_send_dir = 'data/auto_send'
    sends = list()
    for filepath in [auto_send_dir + "/" + filename for filename in os.listdir(auto_send_dir)]:
        lines = list()
        with open(filepath, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        info = {
            '<{|[U]|}>': list(),
            '<{|[D]|}>': list(),
            '<{|[R]|}>': list(),
            '<{|[W]|}>': list(),
        }
        where = ''
        for line in [(line[:-1] if (lines.index(line) != (len(lines) - 1)) else line) for line in lines]:
            if not info.__contains__(line):
                info[where].append(line)
            else:
                where = line
        media = dict()
        for i in info['<{|[R]|}>']:
            parts = i.split('<{|[X]|}>')
            media[parts[0]] = parts[1]
        sends.append({
            'user': info['<{|[U]|}>'][0],
            'dates': info['<{|[D]|}>'],
            'receiver': media,
            'wish_lines': info['<{|[W]|}>']
        })
    print(f'{len(sends)} send plans loaded')
    return sends


def save_auto_send(send: dict):
    if not send.__contains__('user') or not send.__contains__('dates') or not send.__contains__(
            'receiver') or not send.__contains__('wish_lines'):
        print('save rejected')
        raise Exception
    lines = ['<{|[U]|}>\n', send['user'] + '\n', '<{|[D]|}>\n']
    for date in send['dates']:
        lines.append(date + '\n')
    lines.append('<{|[R]|}>\n')
    for media in send['receiver']:
        lines.append(media + '<{|[X]|}>' + str(send['receiver'][media]) + '\n')
    lines.append('<{|[W]|}>\n')
    for line in send['wish_lines']:
        lines.append(line + '\n')
    lines[len(lines) - 1] = lines[len(lines) - 1][:-1]
    auto_send_dir = 'data/auto_send'
    index = len(os.listdir(auto_send_dir)) + 1
    filepath = auto_send_dir + "/" + str(index) + '.plan'
    if os.path.exists(filepath):
        os.remove(filepath)
    with open(filepath, 'x', encoding='utf-8') as file:
        file.writelines(lines)
    print('saved successfully')
    return index


users = load_users()
wish_tweaks = load_wish_tweaks()
wishes = load_wishes()
prefixes = load_prefixes()
disc_config = load_discord_bot_config()
