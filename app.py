from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask import request
from dynamic_scraper import get_piece_info_for_set
from werkzeug.utils import redirect
import csv
import os
import math

COLORS = ["white", "light bluish gray", "light gray", "blue", "dark gray", "dark bluish gray", "black",
            "red", "reddish brown", "brown", "dark brown", "dark tan", "tan",
            "dark nougat", "yellow", "lime", "green", "sand blue", "trans-clear", "trans-red",
            "trans-neon orange", "trans-yellow", "trans-neon-green", "trans-bright-green", "trans-dark-blue",
            "trans-medium blue", "trans-light blue", "trans-light purple", "trans-purple", "trans-dark pink"]

BRICKLINK_COLOR_SET = {"reddish brown": 88}

LIST_OF_SETS = [4735,7113,8089,8036,620,7201,6211,527,6059,7899,6265,4501,7103,6949,6267,7245,7235,8632,4727,3825,4488,4916,8401,6886,6846,4733,7903,7890,6046,6210,6205,6246,7412,7255,7655,1793,7003,4762,6357,7622,8810,7624,4492,7251,10186,10144,7200,6044,7771,7654,7677,6245,4338,7899,4494,4712,8119,7133,8038,7626,8630,6265,4502,7261,7620,4702,7256,7070,6211,4490,7682,6206,7000,4477,6209,7621,4488,6207,4415,6193,6239,7250,7659,8662,10186,4850,4475,7263,7252,4480,6983,6190,7258,8666,7251,4766,6698,6256,4417,7002,6258,6155,1723,4491,4500]
app = Flask(__name__)

# change to name of your database; add path if necessary
db_name = 'pieces.db'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# this variable, db, will be used for all SQLAlchemy commands
db = SQLAlchemy(app)

class Set(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    set_number = db.Column(db.Integer,nullable=False,unique=True)
    num_pieces = db.Column(db.Integer,nullable=False)
    num_pieces_in_use = db.Column(db.Integer,nullable=False)
    percent_pieces_in_use = db.Column(db.Float,nullable=False)
    set_name = db.Column(db.String(20))

class Piece(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    piece_number = db.Column(db.Integer,nullable=False)
    color = db.Column(db.String(20))
    set_number = db.Column(db.Integer, nullable=False)
    is_in_use = db.Column(db.Boolean,nullable=False)

def set_to_dict(set_obj):
    return {"set_number": set_obj.set_number,
            "num_pieces": set_obj.num_pieces,
            "num_pieces_in_use": set_obj.num_pieces_in_use,
            "percent_pieces_in_use": set_obj.percent_pieces_in_use,
            "set_name": set_obj.set_name}

def piece_to_dict(piece_obj):
    return {"set_number": piece_obj.set_number,
            "color": piece_obj.color,
            "piece_number" : piece_obj.piece_number,
            "is_in_use": piece_obj.is_in_use}


@app.route('/')
def home():
    piece_count = Piece.query.count()
    piece_in_use_count = Piece.query.filter_by(is_in_use=True).count()
    piece_count_from_unfinished_sets = 0
    piece_in_use_count_from_unfinished_sets = 0
    for set_obj in Set.query.all():
        if set_obj.percent_pieces_in_use != 100:
            piece_count_from_unfinished_sets += Piece.query.filter_by(set_number = set_obj.set_number).count()
            piece_in_use_count_from_unfinished_sets += Piece.query.filter_by(set_number = set_obj.set_number, is_in_use=True).count()
    return render_template('home.html', piece_count=piece_count, use_count=piece_in_use_count, un_piece_count=piece_count_from_unfinished_sets, un_use_count=piece_in_use_count_from_unfinished_sets)

@app.route('/sets/')
def sets():
    sets = []
    for set_obj in Set.query.all():
        sets.append(set_to_dict(set_obj))
    sets = list(reversed(sorted(sets, key=lambda k: k['percent_pieces_in_use'])))
    return render_template('sets.html', list_of_sets=sets)

@app.route('/submit_piece', methods = ['POST'])
def submit_piece():
    data = request.form
    piece_num = data['piecenum']
    color = data['color']
    sets = {}
    sets_in_use = {}
    if (color == None or color == "") and "," in piece_num:
        color = piece_num.split(",")[1]
        piece_num = piece_num.split(",")[0]
    if color != None and color != "":
        for piece in Piece.query.filter_by(piece_number=piece_num):
            if((piece.color.split(" ", 1)[0]).lower() in color.lower() and color.lower() in piece.color.lower()):
                if not piece.is_in_use:
                    if piece.set_number not in sets:
                        sets[piece.set_number] = [0, set_to_dict(Set.query.filter_by(set_number=piece.set_number).first()),0]
                else:
                    if piece.set_number not in sets:
                        sets[piece.set_number] = [0,set_to_dict(Set.query.filter_by(set_number=piece.set_number).first()),1]
                    else:
                        sets[piece.set_number][2] += 1
                sets[piece.set_number][0] += 1
    else:
        color = ""
        for piece in Piece.query.filter_by(piece_number=piece_num):
            if not piece.is_in_use:
                if piece.set_number not in sets:
                    sets[piece.set_number] = [0, set_to_dict(Set.query.filter_by(set_number=piece.set_number).first()),0,[]]
            else:
                if piece.set_number not in sets:
                    sets[piece.set_number] = [0,set_to_dict(Set.query.filter_by(set_number=piece.set_number).first()),1,[]]
                else:
                    sets[piece.set_number][2] += 1
            if piece.color not in sets[piece.set_number][3]:
                sets[piece.set_number][3].append(piece.color)
            sets[piece.set_number][0] += 1
    keys_to_del = []
    for set_key in sets.keys():
        if sets[set_key][0] == sets[set_key][2]:
            sets_in_use[set_key] = [sets[set_key][0],sets[set_key][1]]
            keys_to_del.append(set_key)

    for key in keys_to_del:
        del sets[key]

    sets_list = []
    similar_pieces = []
    if not sets:
        print("here")
        similar_pieces = list(set(list(map(lambda x: x.piece_number,Piece.query.filter(Piece.piece_number.like("%" + str(piece_num) + "%"))))))
        print(similar_pieces)
    sets_in_use_list = []
    for set_key in sets.keys():
        sets_list.append(sets[set_key])
    for set_key in sets_in_use.keys():
        sets_in_use_list.append(sets_in_use[set_key])
    
    sets_in_use = reversed((sorted(sets_in_use_list, key=lambda x:x[1]['percent_pieces_in_use'])))
    sets = reversed((sorted(sets_list, key=lambda x:x[1]['percent_pieces_in_use'])))
    return render_template('sets_data.html', color=color, piece_num=piece_num, list_of_sets=list(sets), list_of_sets_in_use=sets_in_use, brickLinkColorSet=BRICKLINK_COLOR_SET, similar_pieces=similar_pieces)

@app.route('/add_piece/')
def add_a_piece():
    return render_template('add_a_piece.html')

@app.route('/mark_set_complete/<set_number>', methods = ['POST'])
def mark_set_complete(set_number):
    completed_set=Set.query.filter_by(set_number=set_number).first()
    pieces=Piece.query.filter_by(set_number=set_number)
    completed_set.num_pieces_in_use = completed_set.num_pieces
    completed_set.percent_pieces_in_use = 100

    for piece in pieces:
        piece.is_in_use = True

    db.session.commit()
    sets = []
    for set_obj in Set.query.all():
        sets.append(set_to_dict(set_obj))
    sets = list(reversed(sorted(sets, key=lambda k: k['percent_pieces_in_use'])))
    return render_template('sets.html', list_of_sets=sets)

@app.route('/mark_set_empty/<set_number>', methods = ['POST'])
def mark_set_empty(set_number):
    completed_set=Set.query.filter_by(set_number=set_number).first()
    pieces=Piece.query.filter_by(set_number=set_number)
    completed_set.num_pieces_in_use = 0
    completed_set.percent_pieces_in_use = 0

    for piece in pieces:
        piece.is_in_use = False

    db.session.commit()
    sets = []
    for set_obj in Set.query.all():
        if(set_obj.set_number==6211):
            print(set_obj.percent_pieces_in_use)
        sets.append(set_to_dict(set_obj))
    sets = list(reversed(sorted(sets, key=lambda k: k['percent_pieces_in_use'])))
    return render_template('sets.html', list_of_sets=sets)

@app.route('/submit_piece_to_set', methods = ['POST'])
def submit_piece_to_set():
    data = request.form
    num_pieces = data['num_pieces']
    set_number = data['set_number']
    piece_num = data['piece_number']
    color = data['piece_color']
    set_to_alter = Set.query.filter_by(set_number=set_number).first()
    pieces_to_add = Piece.query.filter_by(piece_number=piece_num, is_in_use=False,set_number=set_number)

    count = 0
    print("Number of Pieces Added:", num_pieces)
    for piece in pieces_to_add:
        if count < int(num_pieces):
            if((piece.color.split(" ", 1)[0]).lower() in color.lower() and color.lower() in piece.color.lower()):
                piece.is_in_use = True
                count += 1
                set_to_alter.num_pieces_in_use += 1
        else:
            break
    
    set_to_alter.percent_pieces_in_use = round((set_to_alter.num_pieces_in_use / set_to_alter.num_pieces)*100,2)

    db.session.commit()
    if(data['back_to_set'] == "true"):
        return redirect('/set/'+set_number)
    else:
        return render_template('add_a_piece.html', quantity=num_pieces,color=color, piece_num=piece_num, set_num=set_number, pct_pieces = set_to_alter.percent_pieces_in_use, is_add = True)
@app.route('/remove_piece_from_set', methods = ['POST'])
def remove_piece_to_set():
    data = request.form
    num_pieces = data['num_pieces']
    set_number = data['set_number']
    piece_num = data['piece_number']
    color = data['piece_color']
    print(set_number)
    set_to_alter = Set.query.filter_by(set_number=set_number).first()
    set_to_alter.num_pieces_in_use = max(set_to_alter.num_pieces_in_use - int(num_pieces),0)
    set_to_alter.percent_pieces_in_use = round((set_to_alter.num_pieces_in_use / set_to_alter.num_pieces) * 100,2)

    pieces_to_add = Piece.query.filter_by(piece_number=piece_num, is_in_use=True,set_number=set_number)

    count = 0
    for piece in pieces_to_add:
        if count < int(num_pieces):
            if((piece.color.split(" ", 1)[0]).lower() in color.lower() and color.lower() in piece.color.lower()):
                piece.is_in_use = False
                count += 1
        else:
            break

    db.session.commit()
    return render_template('added_piece_to_set.html', quantity=num_pieces,color=color, piece_num=piece_num, set_num=set_number, pct_pieces = set_to_alter.percent_pieces_in_use, is_add = False)

@app.route('/set/<set_number>')
def get_set(set_number):
    pieces = {}
    for piece in Piece.query.filter_by(set_number=set_number):
        key = str(piece.piece_number) + piece.color
        if key in pieces and pieces[key][0]["color"] == piece.color:
            pieces[key][1] += 1
        else: 
            pieces[key] = [piece_to_dict(piece),1,0]
        if piece.is_in_use:
            pieces[key][2] += 1
    return render_template('set.html', pieces=pieces, set_number=set_number, percent=Set.query.filter_by(set_number=set_number).first().percent_pieces_in_use)

@app.route('/submit_set', methods = ['POST'])
def submit_set():
    data = request.form
    sets = data['setnum'].split(',')
    for set_num in sets:
        if(Set.query.filter_by(set_number=set_num).first() != None):
            continue
        if(not os.path.isfile('set_data/' + str(set_num) + '.csv')):
            print("here")
            if(len(get_piece_info_for_set(set_num)) == 0):
                continue
        with open('set_data/' + str(set_num) + '.csv', newline='', encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            #add pieces to db below
            count = 0
            for row in reader:
                count += int(row['quantity'])
                for i in range(0,int(row['quantity'])):
                    new_piece = Piece(piece_number=row['reference_number'], color=row['color_and_brick'], set_number=set_num, is_in_use=False)
                    db.session.add(new_piece)
                    db.session.commit()
            # add set
        new_set = Set(set_number=set_num, num_pieces=count, num_pieces_in_use=0, percent_pieces_in_use=0)
        
        db.session.add(new_set)
        db.session.commit()
        name_scraper()
    return redirect('/sets')

@app.route('/add_set/')
def add_a_set():
    return render_template('add_a_set.html')

import urllib
from urllib.request import urlopen
from bs4 import BeautifulSoup
def name_scraper():
    for set_obj in Set.query.filter_by(set_name=None):
        url = "https://www.bricklink.com/v2/catalog/catalogitem.page?S="+ str(set_obj.set_number) + "#T=I"

        hdr = {'User-Agent':'Mozilla/5.0'}

        req = urllib.request.Request(url, headers=hdr)

        page = urlopen(req) 

        soup = BeautifulSoup(page,features="lxml")

        #find elements
        find_all_id = soup.find_all(id='item-name-title')

        print(str(set_obj.set_number))

        set_obj.set_name = find_all_id[0].text

        print(str(set_obj.set_number) + "Set Name: ", set_obj.set_name)
        
        db.session.commit()

if __name__ == '__main__':
    app.run()


def analysis():
    sets = Set.query.all()
    ma = 0
    ma_set = 0
    ma_piece = 0
    for set_obj in sets:
        set_num = set_obj.set_number
        with open('set_data/' + str(set_num) + '.csv', newline='', encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            #add pieces to db below
            count = 0
            for row in reader:
                if(int(row['quantity']) > ma and row['reference_number'] != '3873' and set_obj.percent_pieces_in_use != 100):
                    ma = int(row['quantity'])
                    ma_set = set_num
                    ma_piece = row['reference_number']
                count += int(row['quantity'])
                for i in range(0,int(row['quantity'])):
                    piece = Piece(piece_number=row['reference_number'], color=row['color_and_brick'], set_number=set_num, is_in_use=False)
            # add set
        new_set = Set(set_number=set_num, num_pieces=count, num_pieces_in_use=0, percent_pieces_in_use=0)
        
    return ma, ma_set, ma_piece