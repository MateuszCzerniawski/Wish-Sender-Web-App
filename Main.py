import re

from flask import Flask, request, render_template, redirect, url_for, send_from_directory
import DataLoader
from DataLoader import users, wishes, wish_tweaks, prefixes
import WishEditor as we
from GPTcontroller import gpt
from DiscordBot import DiscordBot
from SendPlanner import SendPlanner

discord = DiscordBot()
planner = SendPlanner()
planner.discord_bot = discord
app = Flask(__name__)


@app.route('/')
def login_page():
    return render_template('login.html')


@app.route('/login_redirect')
def login_redirect():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def log_in():
    username = request.form.get('username')
    print(request.form.get('login_option'))
    if request.form.get('login_option') == 'user' and users.__contains__(username) and users[
        username] == request.form.get('password'):
        return redirect(url_for('home', username=username, login_option='user'))
    elif request.form.get('login_option') == 'guest':
        return redirect(url_for('home', username=username, login_option='guest'))
    else:
        return render_template('login.html', error='Invalid username or password. Please try again.')


@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = data['password']
    if users.__contains__(username):
        return 'User already exists', 400
    users[username] = password
    DataLoader.save_user(username, password)
    return 'Registered', 204


@app.route('/home/<username>')
def home(username):
    return render_template('main.html', username=username)


@app.route('/assets/images/<image>')
def test(image):
    return send_from_directory('assets/images', image)


@app.route('/archive/<username>')
def archive_page(username):
    return render_template('archive.html', username=username, wishes=wishes, tweaks=wish_tweaks)


@app.route('/wish/replace', methods=['POST'])
def replace_in_wish():
    data = request.json
    print('request for replace:', data)
    return we.get_wish(data['wish_category'], data['wish_filename'], replacements=data['repl'])


@app.route('/prefixfor/<wish_type>')
def get_prefix_for(wish_type):
    return prefixes[wish_type]


@app.route('/send', methods=['POST'])
def send_attempt():
    data = request.json
    if ('login_option' not in data) or (data['login_option'] != 'user'):
        return url_for('login_redirect')
    login_option = data['login_option']
    username = data['username']
    wish = data['wish']
    return url_for('send_page', username=username, wish=wish, login_option=login_option)


@app.route('/send_page', methods=['GET'])
def send_page():
    username = request.args.get('username')
    wish = request.args.get('wish')
    login_option = request.args.get('login_option')
    return render_template('send.html', wish=wish, username=username, login_option=login_option), 200


@app.route('/send/now', methods=['GET', 'POST'])
def send_now():
    data = request.json
    discord_id = int(data['discord_id']) if ('discord_id' in data and data['discord_id'] != '') else 0
    wish = data['wish'] if 'wish' in data else ''
    platforms = re.split(',', data['platforms']) if 'platforms' in data else list()
    if platforms.__contains__('Discord'):
        print('sending via Discord')
        discord_result = discord.send(discord_id, wish)
        if discord_result == 'sent':
            return render_template('send_successfull.html', username=data['username'])
    return 'You (probably not intentionally) didn\'t fill form correctly. Click <- on your browser and try again', 200


@app.route('/send/plan', methods=['POST'])
def plan_send():
    data = request.json
    username = data['username']
    try:
        planner.save_plan(data)
        return render_template('plan_creation_success.html', username=username)
    except:
        return 'You (probably not intentionally) didn\'t fill form correctly. Click <- on your browser and try again', 200


@app.route('/wish/generate/<prefix>')
def gen_wish(prefix):
    print(prefix)
    return gpt.generate(prefix)


@app.route('/planned/<username>')
def show_planned(username):
    planned = planner.get_planned_by(username)
    return render_template('planned.html', username=username, planned=planned)


app.run(debug=False)
