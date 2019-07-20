# -*- coding: UTF-8 -*-

# Description: comment
#      Author: zhangxingkui
#    Datetime: 2019-07-20 08:24


from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,
    session, current_app)
from werkzeug.exceptions import abort

from CommentChain.auth import login_required
from CommentChain.db import get_db

bp = Blueprint('comment', __name__, url_prefix='/comment')


def get_seller_id():
    post = get_db().execute(
        'SELECT id FROM user WHERE username = \'seller\'',
        # (id,)
    ).fetchone()

    if post is None:
        current_app.logger.debug("get seller id error.")

    return post["id"]


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    """
    点击购买后跳转创建评论页面
    :return:
    """
    user_id = g.user['id']
    deal = get_db().execute(
        'select * from comment where user_id = ?', (user_id,)
    ).fetchall()
    current_app.logger.debug(f"user {user_id} wether add comment: {len(deal)}")

    if len(deal) > 0:
        flash("已经评论过")
        return redirect(url_for("goods.detail"))

    if request.method == 'POST':

        comment_body = request.form['comment']
        comment_stars = request.form['stars']
        error = None

        if not comment_body:
            error = 'comment is required.'

        if not comment_stars:
            error = 'comment is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO comment (user_id, comment, stars)'
                ' VALUES (?, ?, ?)',
                (session['user_id'], comment_body, comment_stars)
            )
            db.commit()

            return redirect(url_for('goods.detail'))

    seller_id = get_seller_id()
    # price = request.form['price']
    price = 65
    error = None

    if not seller_id:
        error = 'seller_id is required.'
    if not price:
        error = 'price is required.'

    if error is not None:
        flash(error)
    else:
        db = get_db()
        db.execute(
            'INSERT INTO deal (user_id, receiver_id, price)'
            ' VALUES (?, ?, ?)',
            (session['user_id'], seller_id, price)
        )
        db.commit()

    return render_template("comment/comment.html")
