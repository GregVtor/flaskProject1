import datetime

from flask import Flask, render_template, request, redirect, make_response, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///base'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = "False"
db = SQLAlchemy(app)
clas = ''
chel = ''
mat = 0
book = []

app.app_context().push()


class User(db.Model):
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer(), primary_key=True)
    nf = db.Column(db.String(50), nullable=False)
    login = db.Column(db.String(8), nullable=False, unique=True)
    password = db.Column(db.String(12), nullable=False)
    types = db.Column(db.String(9), nullable=False)
    class_us = db.Column(db.String(9), nullable=True)
    user = db.relationship('History')

    def __init__(self, nf, login, password, types, class_us):
        self.nf = nf
        self.login = login
        self.password = password
        self.types = types
        self.class_us = class_us
        self.date = datetime.datetime.now()

    def __repr__(self):
        return self.class_us


class Books(db.Model):
    __tablename__ = 'books'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(50), nullable=False)
    quantily = db.Column(db.Integer(), nullable=False)
    types = db.Column(db.String(9), nullable=False)
    book = db.relationship('History')

    def __init__(self, title, author, quantily, types):
        self.title = title
        self.author = author
        self.quantily = quantily
        self.types = types

    def __repr__(self):
        return str(self.id)


class History(db.Model):
    __tablename__ = 'history'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    book_id = db.Column(db.Integer(), db.ForeignKey('books.id'))
    date = db.Column(db.DateTime, default=datetime.datetime.now())
    status = db.Column(db.Integer(), nullable=False)

    def __init__(self, user_id, book_id, status):
        self.user_id = user_id
        self.book_id = book_id
        self.status = status
        self.date = datetime.datetime.now()

    def __repr__(self):
        return str(self.id)


db.create_all()


@app.route('/')
def main_page():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        n = request.form["name"]
        f = request.form["last_name"]
        login = request.form["login"]
        password = request.form["password"]
        types = request.form["types"]
        class_us = request.form["class_us"]
        if class_us:
            pass
        else:
            class_us = None
        if db.session.query(User).filter(User.login == login).all():
            return redirect(url_for('register'))
        else:
            c = User(f'{n} {f}', login, password, types, class_us)
            db.session.add(c)
            db.session.commit()
            return redirect(url_for('main_page'))
    else:
        return render_template('register.html')


@app.route('/entrance', methods=['GET', 'POST'])
def entrance():
    if request.cookies.get('login'):
        return redirect(url_for('looking'))
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        try:
            if password == db.session.query(User).filter_by(login=login).first().password:
                res = make_response(redirect(url_for('looking')))
                res.set_cookie('login', login, 3600)
                return res
            else:
                return redirect(url_for('entrance'))
        except:
            return redirect(url_for('entrance'))
    else:
        return render_template('entrance.html')


@app.route('/main', methods=['GET', 'POST'])
def looking():
    login = request.cookies.get('login')
    classes = list(set(str(i) for i in db.session.query(User).all()))
    classes = [i for i in classes if i != 'TH']
    classes = sorted(classes, key=lambda x: (x[0], x[1:]))
    users = {}
    res = make_response(redirect(url_for('looking')))
    global clas, chel, book, mat
    for i in classes:
        users[i] = [i.nf for i in db.session.query(User).filter(User.class_us == i).all()]
    if not login:
        return redirect('entrance')
    if db.session.query(User).filter_by(login=login).first().types == 'librarian':
        if request.method == 'POST':
            try:
                clas = request.form['clas']
                mat = 0
                book = []
                ids = [str(i.id) for i in db.session.query(User).filter_by(class_us=clas).all()]
                for i in ids:
                    for j in db.session.query(History).filter_by(user_id=i).all():
                        if j.status:
                            b = db.session.query(Books).filter_by(id=j.book_id).first()
                            book.append([b.title, b.author, 1, b.id, 0, ''])
                dic = {}
                mark = 1
                for i in range(len(book)):
                    for j in range(len(book)):
                        for n in dic.values():
                            for g in n:
                                if i == g:
                                    mark = 0
                                elif mark:
                                    mark = 1
                        if i != j and book[i][:-1] == book[j][:-1] and mark and i not in dic.keys():
                            dic[i] = [j]
                        elif i != j and book[i][:-1] == book[j][:-1] and mark:
                            dic[i].append(j)
                        mark = 1
                for i in dic.keys():
                    for j in dic[i]:
                        book[i][2] += 1
                        book[j] = ''
                delta = []
                for i in book:
                    if i != '':
                        delta.append(i)
                book = delta
                col = 1
                for i in book:
                    i.insert(0, col)
                    col += 1
            except:
                pass
            try:
                chel = request.form['chel']
                mat = 1
                id = db.session.query(User).filter_by(nf=chel, class_us=clas).first().id
                history = []
                col = 1
                for i in db.session.query(History).filter_by(user_id=id).all():
                    n = db.session.query(History).filter_by(id=str(i)).first().book_id
                    if db.session.query(History).filter_by(id=str(i)).first().status:
                        h = db.session.query(Books).filter_by(id=n).first()
                        history.append([h.title, h.author, 1, h.id, 1, id])
                dic = {}
                mark = 1
                for i in range(len(history)):
                    for j in range(len(history)):
                        for n in dic.values():
                            for g in n:
                                if i == g:
                                    mark = 0
                                elif mark:
                                    mark = 1

                        if i != j and history[i][:-1] == history[j][:-1] and mark and i not in dic.keys():
                            dic[i] = [j]
                        elif i != j and history[i][:-1] == history[j][:-1] and mark:
                            dic[i].append(j)
                        mark = 1
                for i in dic.keys():
                    for j in dic[i]:
                        history[i][2] += 1
                        history[j] = ''
                for i in history:
                    if i == '':
                        del history[history.index(i)]
                col = 1
                for i in history:
                    i.insert(0, col)
                    col += 1
                book = history
            except:
                pass
            try:
                out = request.form['out']
                mat = 0
            except:
                out = 0
            if out:
                res = make_response(redirect('/'))
                res.set_cookie('login', '', 0)
                return res
            try:
                book_zda, user_book = request.form['diz'].split()
                h = db.session.query(History).filter_by(user_id=user_book, book_id=book_zda, status=1).first()
                b = db.session.query(Books).filter_by(id=book_zda).first()
                b.quantily += 1
                h.status = 0
                db.session.commit()
                id = db.session.query(User).filter_by(nf=chel, class_us=clas).first().id
                history = []
                col = 1
                for i in db.session.query(History).filter_by(user_id=id).all():
                    n = db.session.query(History).filter_by(id=str(i)).first().book_id
                    if db.session.query(History).filter_by(id=str(i)).first().status:
                        h = db.session.query(Books).filter_by(id=n).first()
                        history.append([h.title, h.author, 1, h.id, 1, id])
                dic = {}
                mark = 1
                for i in range(len(history)):
                    for j in range(len(history)):
                        for n in dic.values():
                            for g in n:
                                if i == g:
                                    mark = 0
                                elif mark:
                                    mark = 1

                        if i != j and history[i][:-1] == history[j][:-1] and mark and i not in dic.keys():
                            dic[i] = [j]
                        elif i != j and history[i][:-1] == history[j][:-1] and mark:
                            dic[i].append(j)
                        mark = 1
                for i in dic.keys():
                    for j in dic[i]:
                        history[i][2] += 1
                        history[j] = ''
                for i in history:
                    if i == '':
                        del history[history.index(i)]
                col = 1
                for i in history:
                    i.insert(0, col)
                    col += 1
                book = history
            except:
                pass
            return res
        print(classes, users, clas, book, mat)
        return render_template('main_librarian.html', classes=classes, users=users, m=clas, book=book, mat=mat)
    elif db.session.query(User).filter_by(login=login).first().types == 'student':
        nf = db.session.query(User).filter_by(login=login).first().nf
        clas = db.session.query(User).filter_by(login=login).first().class_us
        id = db.session.query(User).filter_by(login=login).first().id
        history = []
        col = 1
        for i in db.session.query(History).filter_by(user_id=id).all():
            n = db.session.query(History).filter_by(id=str(i)).first().book_id
            if db.session.query(History).filter_by(id=str(i)).first().status:
                history.append([db.session.query(Books).filter_by(id=n).first().title,
                                db.session.query(Books).filter_by(id=n).first().author, 1])
        dic = {}
        mark = 1
        for i in range(len(history)):
            for j in range(len(history)):
                for n in dic.values():
                    for g in n:
                        if i == g:
                            mark = 0
                        elif mark:
                            mark = 1

                if i != j and history[i][:-1] == history[j][:-1] and mark and i not in dic.keys():
                    dic[i] = [j]
                elif i != j and history[i][:-1] == history[j][:-1] and mark:
                    dic[i].append(j)
                mark = 1
        for i in dic.keys():
            for j in dic[i]:
                history[i][2] += 1
                history[j] = ''
        for i in history:
            if i == '':
                del history[history.index(i)]
        col = 1
        for i in history:
            i.insert(0, col)
            col += 1
        try:
            out = request.form['out']
        except:
            out = 0
        if out:
            res = make_response(redirect('/'))
            res.set_cookie('login', '', 0)
            return res
        return render_template('main_user.html', his=history)
    elif db.session.query(User).filter_by(login=login).first().types == 'teacher':
        class_us = db.session.query(User).filter_by(login=login).first().class_us
        users = [i.nf for i in db.session.query(User).filter(User.class_us == class_us, User.types != "teacher").all()]
        if request.method == 'POST':
            try:
                clas = request.form['clas']
                book = []
                ids = [str(i.id) for i in db.session.query(User).filter_by(class_us=clas).all()]
                for i in ids:
                    for j in db.session.query(History).filter_by(user_id=i).all():
                        if j.status:
                            book.append(
                                [db.session.query(Books).filter_by(id=j.book_id).first().title,
                                 db.session.query(Books).filter_by(id=j.book_id).first().author, 1])
                dic = {}
                mark = 1
                for i in range(len(book)):
                    for j in range(len(book)):
                        for n in dic.values():
                            for g in n:
                                if i == g:
                                    mark = 0
                                elif mark:
                                    mark = 1
                        if i != j and book[i][:-1] == book[j][:-1] and mark and i not in dic.keys():
                            dic[i] = [j]
                        elif i != j and book[i][:-1] == book[j][:-1] and mark:
                            dic[i].append(j)
                        mark = 1
                for i in dic.keys():
                    for j in dic[i]:
                        book[i][2] += 1
                        book[j] = ''
                delta = []
                for i in book:
                    if i != '':
                        delta.append(i)
                book = delta
                col = 1
                for i in book:
                    i.insert(0, col)
                    col += 1
            except:
                pass
            try:
                chel = request.form['chel']
                print(chel)
                id = db.session.query(User).filter_by(nf=chel, class_us=clas).first().id
                history = []
                col = 1
                for i in db.session.query(History).filter_by(user_id=id).all():
                    n = db.session.query(History).filter_by(id=str(i)).first().book_id
                    if db.session.query(History).filter_by(id=str(i)).first().status:
                        history.append([db.session.query(Books).filter_by(id=n).first().title,
                                        db.session.query(Books).filter_by(id=n).first().author, 1])
                dic = {}
                mark = 1
                for i in range(len(history)):
                    for j in range(len(history)):
                        for n in dic.values():
                            for g in n:
                                if i == g:
                                    mark = 0
                                elif mark:
                                    mark = 1

                        if i != j and history[i][:-1] == history[j][:-1] and mark and i not in dic.keys():
                            dic[i] = [j]
                        elif i != j and history[i][:-1] == history[j][:-1] and mark:
                            dic[i].append(j)
                        mark = 1
                for i in dic.keys():
                    for j in dic[i]:
                        history[i][2] += 1
                        history[j] = ''
                for i in history:
                    if i == '':
                        del history[history.index(i)]
                col = 1
                for i in history:
                    i.insert(0, col)
                    col += 1
                book = history
            except:
                pass
            try:
                out = request.form['out']
            except:
                out = 0
            if out:
                res = make_response(redirect('/'))
                res.set_cookie('login', '', 0)
                return res
            return redirect(url_for('looking'))
        print(book)
        return render_template('main_teacher.html', users=users, i=class_us, book=book)
    return redirect('entrance')


@app.route('/books', methods=['GET', 'POST'])
def books():
    if not request.cookies.get('login') or db.session.query(User).filter_by(
            login=request.cookies.get('login')).first().types != 'librarian':
        return redirect(url_for('entrance'))
    if request.method == 'POST':
        title, author, quantily, types = request.form['title'], request.form['author'], request.form['quantily'], \
        request.form['types']
        c1 = Books(title, author, quantily, types)
        db.session.add(c1)
        db.session.commit()
        return redirect(url_for('looking'))
    return render_template('book.html')


@app.route('/add_book', methods=['POST', 'GET'])
def add_book():
    login = request.cookies.get('login')
    try:
        n = db.session.query(User).filter_by(nf=chel, class_us=clas).first().id
    except:
        return redirect("/main")
    book = []
    for i in db.session.query(Books).filter(Books.quantily != 0).all():
        book.append((i.title, i.id))
    if not login:
        return redirect("/entrance")
    if db.session.query(User).filter_by(login=login).first().types == 'librarian':
        if request.method == 'POST':
            booke = request.form.getlist('books')
            for i in booke:
                c1 = History(n, i, 1)
                b = db.session.query(Books).filter_by(id=i).first()
                b.quantily -= 1
                db.session.add(c1)
                db.session.commit()
            return redirect('main')
        return render_template('add_book.html', books=book)
    return redirect('/')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8080')
