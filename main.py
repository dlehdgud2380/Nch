#!/usr/bin/env python
#coding: utf-8

import os
#import ssl
import json
from flask import Flask, render_template, session
from flask_socketio import SocketIO, emit

app = Flask(__name__, template_folder='templates')
app.secret_key = 'secret_key'
socketio = SocketIO(app)

user_no = 1
user_list = []
user_name=[]

@app.before_request
def before_request():
    global user_no
    global user_list
    if 'session' in session and 'user-id' in session:
      pass
    else:
      session['session'] = os.urandom(24)
      session['username'] = '시민'+str(user_no)
      user_list.append(session['username'])
      user_no += 1

@app.route('/')
def index():
  return render_template("index.html")

@app.route('/test')
def test():
  return render_template("test.html")

@socketio.on('connect', namespace='/chatroom')
def connect():
  print(session['username'] + " is Connected")
  emit("response", {'data': "(접속)" , 'username': session['username'], 'userlist' : user_list}, broadcast=True)
@socketio.on('disconnect', namespace='/chatroom')
def disconnect():
  print(session['username'] + " is Disconnected")
  emit("response", {'data': "(접속해제)", 'username': session['username'], 'userlist' : user_list}, broadcast=True)
  user_list.remove(session['username'])
  session.clear()

#메시지 request 처리
@socketio.on("request", namespace='/chatroom') 

def request(message):
  print("GET: %s" %message)
  print("유저목록: %s" %user_list)

  #채팅봇
  class BotMsg:
    def __init__(self, getdata):
      self.data = getdata
    def bothelp(self):
      username = "nch@bot"
      data = "\n /chne + 닉네임 : 닉네임 변경 \n /music: (미구현)\n /info : nch및 개발자 정보"
      return (username, data)
    def changename(self):
      data = json.dumps(self.data.get('data'),ensure_ascii=False)[7:][:-1]
      if session['username'] in user_list:
        user_list.remove(session['username'])
        session['username'] = data
        user_list.append(data)
    def info(self):
      username = "nch@bot"
      data = "\n Nch ver: Beta 0.1 \n 개발자: Sc0_ネプ \n 이 채팅페이지는 Python 3.7 + Flask기반으로 운영되고 있습니다."
      return (username, data)
      

  #채팅봇 메시지
  Bot = BotMsg(message)
  if message == {'data': '/help'}:
    emit("response", {'data': message['data'], 'username': session['username'], 'userlist' : user_list}, broadcast=True)
    emit("response", {'data': Bot.bothelp()[1], 'username': Bot.bothelp()[0]}, broadcast=True)
  #채팅접속을 종료했을 때 처리
  elif message == {'data': '#Disconnected*'}:
    disconnect()
    emit("response", {'data': "온라인 목록 업데이트", 'username': "nch@bot", 'userlist' : user_list}, broadcast=True)
  elif message == {'data': '/info'}:
    emit("response", {'data': message['data'], 'username': session['username'], 'userlist' : user_list}, broadcast=True)
    emit("response", {'data': Bot.info()[1], 'username': "nch@bot", 'userlist' : user_list}, broadcast=True)
  #닉네임변경 요청 했을 때
  elif "/chne" in json.dumps(message):
    if json.dumps(message)[15]==" ":
      prename = session['username']
      Bot.changename()
      newname = session['username']
      emit("response", {'data': "('{0}'에서 '{1}'로 닉네임변경)".format(prename, newname), 'username': "nch@bot", 'userlist' : user_list}, broadcast=True)
    else:
      emit("response", {'data': "/chne + 닉네임 : 닉네임 변경", 'username': "nch@bot", 'userlist' : user_list}, broadcast=True)
  #일반적인 메시지 처리
  else:
    emit("response", {'data': message['data'], 'username': session['username'], 'userlist' : user_list}, broadcast=True)

if __name__ == '__main__':
  #ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
  #ssl_context.load_cert_chain(certfile='newcert.pem', keyfile='newkey.pem', password='secret')
  #socketio.run(app(ssl_context=ssl_context), host='0.0.0.0', port=5000, debug=True)
  socketio.run(app, host='0.0.0.0', port=5000, debug=True)

'''
#linux terminal access in repl.it

import os

while True:
  os.system(input(">"))
'''