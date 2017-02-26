from flask import render_template, Flask, session, redirect, url_for, request, g, send_file
from tabletOfSale import app, get_db
import sqlite3
import pkg_resources

@app.route('/css/<css>')
def css(css):
	return send_file(pkg_resources.resource_filename('tabletOfSale.views', 'css/' + css), mimetype='text/css')

@app.route('/js/<js>')
def js(js):
	return send_file(pkg_resources.resource_filename('tabletOfSale.views', 'js/' + js), mimetype='text/javascript')

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method=='POST':
		cur=get_db().cursor()
		t=(request.form['pin'],)
		data=cur.execute('select rowid from Staff where pin=?', t).fetchall()
		if len(data)==1:
			session['staff_id']=data[0]
			clk=(str(session['staff_id']),)
			cur.execute('update Staff set clocked_in=1 where rowid=?', clk)
			cur.execute("insert into Shift_Log values (?, 1, datetime('now'))", clk)
			get_db().commit()
			return redirect(url_for('index'))
	return render_template('login.html')

@app.route('/')
def index():
	if 'staff_id' in session:
		cur=get_db().cursor()
		t=(str(session['staff_id'][0]),)
		parties=cur.execute("select rowid, table_id from Party where staff_id=" + str(session['staff_id'][0]) + " and datetime_out is null").fetchall()
		menu=cur.execute("select rowid, name, price from Menu").fetchall()
		return render_template('index.html', parties=parties, menu=menu)
	return redirect(url_for('login'))

@app.route('/logout')
def logout():
	cur=get_db().cursor()
	t=(str(session['staff_id']),)
	cur.execute('update Staff set clocked_in=0 where rowid=?', t)
	cur.execute("insert into Shift_Log values (?, 0, datetime('now'))", t)
	get_db().commit()
	session.pop('staff_id', None)
	return redirect(url_for('login'))

@app.route('/party/<party_id>')
def party_view(party_id):
	cur=get_db().cursor()
	t=(party_id,)
	people=cur.execute("select distinct person_id from Orders where party_id=?", t).fetchall()
	return render_template('party.html', people=people)

@app.route('/party/<party_id>/<person_id>')
def person_view(party_id, person_id):
	cur=get_db().cursor()
	t=(party_id, person_id)
	items=cur.execute("select name, price from Menu where rowid in (select menu_id from Orders where party_id=? and person_id=?)", t).fetchall()
	return render_template('person.html', items=items)

@app.route('/party/<party_id>/menu')
def menu_view(party_id):
	cur=get_db().cursor()
	items=cur.execute('select rowid, name, price from Menu').fetchall()
	return render_template('menu.html', items=items)

@app.route('/party/<party_id>/menu/add', methods=['POST'])
def menu_add(party_id):
	cur=get_db().cursor()
	t=(party_id, request.form['menu_id'], request.form['person_id'])
	cur.execute('insert into Orders values (?, ?, ?)', t)
	get_db().commit()
	return redirect(url_for('menu_view'))
