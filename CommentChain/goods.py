# -*- coding: UTF-8 -*-

# Description: goods
#      Author: zhangxingkui
#    Datetime: 2019-07-20 15:41
from datetime import datetime, timedelta

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,
    session, current_app)
from werkzeug.exceptions import abort

from CommentChain.auth import login_required
from CommentChain.db import get_db

bp = Blueprint('goods', __name__, url_prefix='/goods')


@bp.route('/list_all', methods=('GET',))
@login_required
def list_all():
    return render_template('goods/goods.html')


def get_user_name(user_id):
    username = get_db().execute(
        'SELECT username'
        ' FROM user where id = ?', (user_id,)
    )
    return username

def dict_factory(cursor, row):
    return dict((col[0], row[idx]) for idx, col in enumerate(cursor.description))


def get_all_comments():
    db = get_db()
    db.row_factory = dict_factory

    comments = db.execute(
        'SELECT c.id, user_id, u.username, created, comment, stars from comment c join'
        ' user u on c.user_id = u.id ',
    ).fetchall()

    # 查询是否有'退款'记录，然后计算
    for comment in comments:
        # 查询购买记录
        user_id = comment['user_id']
        order_deal = db.execute(
            'select * from deal where user_id = ?', (user_id,)
        ).fetchone()

        if order_deal is None:
            current_app.logger.debug("get comment deal error")

        # 查询退款记录
        receiver_id = comment['user_id']
        user_id = get_seller_id()
        back_deal = db.execute(
            'SELECT * FROM deal WHERE user_id = ? AND receiver_id = ?', (user_id, receiver_id)
        ).fetchone()
        if back_deal is not None:
            if order_deal['price'] == back_deal['price']:
                # 计算币天，标记退款
                comment['back'] = True
                delta = back_deal['created'] - order_deal['created']
                current_app.logger.debug(f"coin delta date: {delta}")
                comment['coin_day'] = int(delta.total_seconds() * int(order_deal['price']) / timedelta(days=1).total_seconds() * 100)
                continue

        # 计算本评论的币天
        delta = datetime.now() - order_deal['created']
        current_app.logger.debug(f"coin delta date: {delta}")
        comment['coin_day'] = int(delta.total_seconds() * int(order_deal['price']) / timedelta(days=1).total_seconds() * 100)

    if comments is None:
        current_app.logger.debug("get comments error.")

    current_app.logger.debug(f"comments: {comments}")

    return comments


@bp.route('/detail', methods=('GET',))
@login_required
def detail():
    return render_template('goods/things.html', comments=get_all_comments())


# @bp.route('/buy', methods=('GET', 'POST'))
# @login_required
# def buy():
#     if request.method == 'POST':
#         seller_id = get_seller_id()
#         # price = request.form['price']
#         price = 123
#         error = None
#
#         if not seller_id:
#             error = 'seller_id is required.'
#         if not price:
#             error = 'price is required.'
#
#         if error is not None:
#             flash(error)
#         else:
#             db = get_db()
#             db.execute(
#                 'INSERT INTO deal (user_id, receiver_id, price)'
#                 ' VALUES (?, ?, ?)',
#                 (session['user_id'], seller_id, price)
#             )
#             db.commit()
#             return redirect(url_for('comment.create'))
#
#     return redirect(url_for('goods.detail'))


def get_seller_id():
    post = get_db().execute(
        'SELECT id FROM user WHERE username = \'seller\'',
        # (id,)
    ).fetchone()

    if post is None:
        current_app.logger.debug("get seller id error.")

    return post["id"]


def get_deal(id):
    db = get_db()
    deal = db.execute(
        'SELECT user_id, receiver_id, price FROM deal'
        ' WHERE id = ?',
        (id,)
    ).fetchone()
    return deal


@bp.route('/<int:id>/back', methods=('POST',))
@login_required
def back(id):
    """
    退款，记录退款数据到交易记录里
    """

    back_deal = get_deal(id)
    current_app.logger.debug(f"back deal {id}")
    db = get_db()
    db.execute(
        'INSERT INTO deal (user_id, receiver_id, price)'
        ' VALUES (?, ?, ?)',
        (back_deal['receiver_id'], back_deal['user_id'], back_deal['price'])
    )
    db.commit()

    return redirect(url_for('goods.detail'))


def get_seller_deals():
    seller_id = get_seller_id()
    deals = get_db().execute(
        'SELECT id, user_id, receiver_id, created, price'
        ' FROM deal WHERE receiver_id = ?', (seller_id,)
    ).fetchall()

    if deals is None:
        current_app.logger.debug("get deal error")
    current_app.logger.debug(f"get deal :{deals}")

    return deals


@bp.route('/seller', methods=('GET',))
@login_required
def seller():
    return render_template('goods/seller.html', deals=get_seller_deals())
