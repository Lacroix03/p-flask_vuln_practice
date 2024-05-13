from flask import Flask, session, render_template, request, redirect, g, url_for, jsonify, make_response
import pymysql
import os

app = Flask(__name__)

#db연결
db = pymysql.connect(host='127.0.0.1', port = 2222, user='root', password='211202', db='db', charset = 'utf8')
cursor = db.cursor() 

app.secret_key = "ABC"

def get_user_info(user_id):
    # 사용자 ID를 기반으로 DB에서 사용자 정보를 가져오는 쿼리를 실행
    sql = "SELECT * FROM users WHERE username = %s;"
    cursor.execute(sql, (user_id))
    user_info = cursor.fetchone()  # 사용자 정보를 가져옴
    return user_info

def get_board(board_index):
    sql = "SELECT * from board where num = %s;"
    cursor.execute(sql,(board_index))
    board_info = cursor.fetchone()
    return board_info

@app.route('/',methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user', None)
        _id = request.form['userID']
        _password = request.form['password']
        sql ="select * from users where userid= '%s' and userpw = '%s'" % (_id, _password)
        cursor.execute(sql)
        result = cursor.fetchone()
        if result:
            session['user'] = result[0]
            return redirect(url_for('main'))
        else:
            return '<script>alert("로그인 실패.");location.href="/"</script>'
    return render_template('login.html')
    
@app.route('/signup',methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        _name = request.form['inputname']
        _id = request.form['userID']
        _password = request.form['password']
        _email = request.form['inputemail']
        _value = (_name, _id, _password, _email)
        #db에 insert
        sql ="insert into users(username, userid, userpw, email) values (%s, %s, %s, %s);"
        try:
            cursor.execute(sql, _value)
            db.commit()
        except :
            return '<script>alert("중복된 ID입니다.");location.href="/signup"</script>'
        return redirect(url_for('login'))
    else:
        return render_template('signup.html')

@app.route('/board',methods=['GET'])
def board():
    sql = "SELECT * from board"
    cursor.execute(sql)
    data_list = cursor.fetchall()
    return render_template("board.html", data_list=data_list)

@app.route('/boardview/<int:board_index>', methods=['GET'])
def boardview(board_index):
    board_info = get_board(board_index)
    sql = "update board set views = views+1 where num = %s;"
    cursor.execute(sql, board_index)
    db.commit()
    return render_template('boardview.html', board_info=board_info)

@app.route('/write',methods=['GET', 'POST'])
def write():
    if g.user:
        if request.method == 'POST':
            _title = request.form['title']
            _content = request.form['contents']
            _writer = session.get('user')
            _view = 0
            _value = (_title, _content, _writer, _view)
            #db에 insert
            sql ="insert into board(title, contents, writer, views) values (%s, %s, %s, %s);"
            cursor.execute(sql, _value)
            db.commit()
            return redirect(url_for('board'))
        else:
            return render_template('write.html')
    else:
        return '<script>alert("로그인 먼저 해주세요.");location.href="/"</script>'
    
@app.route('/info',methods=['GET'])
def info():
    return render_template("info.html")

@app.route('/mypage',methods=['GET'])
def mypage():
    # 세션에서 현재 로그인된 사용자의 ID를 가져옴 (예시로 'current_user'로 가정)
    current_user_id = session.get('user')
    if current_user_id :
        user_info = get_user_info(current_user_id)
        return render_template('mypage.html', user_info=user_info)
    else :
        return render_template('login.html')

@app.route('/main')
def main():
    if g.user:
        return render_template("main.html",user=session['user'])
    else:
        return redirect(url_for('login'))

@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)