from flask import Flask, render_template, redirect, url_for, request, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Memo
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secretkey"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///memos.db'
db.init_app(app)

# 註冊頁面
@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(username=username, password=hashed_password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful!")
            return redirect(url_for('login'))
        except:
            flash("Username already exists.")
    return render_template('register.html')

# 登入頁面
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash("Login successful!")
            return redirect(url_for('home'))
        else:
            flash("Invalid credentials.")
    return render_template('login.html')

# 主頁（備忘錄列表）
@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    memos = Memo.query.filter_by(user_id=user.id).all()
    return render_template('home.html', memos=memos)

# 新增備忘錄
@app.route('/add_memo', methods=['GET', 'POST'])
def add_memo():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        content = request.form['content']
        new_memo = Memo(content=content, user_id=session['user_id'])
        
        try:
            db.session.add(new_memo)
            db.session.commit()
            flash("Memo added successfully!")
            return redirect(url_for('home'))
        except:
            flash("Failed to add memo.")
    return render_template('add_memo.html')

# 編輯備忘錄
@app.route('/edit_memo/<int:id>', methods=['GET', 'POST'])
def edit_memo(id):
    memo = Memo.query.get_or_404(id)
    
    if request.method == 'POST':
        memo.content = request.form['content']
        
        try:
            db.session.commit()
            flash("Memo updated successfully!")
            return redirect(url_for('home'))
        except:
            flash("Failed to update memo.")
    return render_template('edit_memo.html', memo=memo)

# 刪除備忘錄
@app.route('/delete_memo/<int:id>')
def delete_memo(id):
    memo = Memo.query.get_or_404(id)
    
    try:
        db.session.delete(memo)
        db.session.commit()
        flash("Memo deleted successfully!")
        return redirect(url_for('home'))
    except:
        flash("Failed to delete memo.")

# 登出
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Logged out successfully!")
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
