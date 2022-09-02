# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
from functools import wraps

from flask import g, current_app, request
from authlib.jose import jwt, JoseError
from todoism.apis.v1.errors import api_abort, invalid_token, token_missing
from todoism.models import User


def generate_token(user):
    expiration = 3600
    # 签名算法
    header = {'alg': 'HS256'}
    # 用于签名的密钥
    key = current_app.config['SECRET_KEY']
    data = {'id': user.id}
    token = jwt.encode(header=header, payload=data, key=key).decode('ascii')
    return token, expiration


def validate_token(token):
    key = current_app.config['SECRET_KEY']
    try:
        data = jwt.decode(token, key)
    except JoseError:
        return False
    user = User.query.get(data['id'])
    if user is None:
        return False
    g.current_user = user
    return True


def get_token():
    # Flask/Werkzeug do not recognize any authentication types
    # other than Basic or Digest, so here we parse the header by hand.
    if 'Authorization' in request.headers:
        try:
            token_type, token = request.headers['Authorization'].split(None, 1)
        except ValueError:
            # The Authorization header is either empty or has no token
            token_type = token = None
    else:
        token_type = token = None

    return token_type, token


# 登录保护装饰器
def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # 获取令牌类型和令牌
        token_type, token = get_token()

        # Flask normally handles OPTIONS requests on its own, but in the
        # case it is configured to forward those to the application, we
        # need to ignore authentication headers and let the request through
        # to avoid unwanted interactions with CORS.
        if request.method != 'OPTIONS':
            if token_type is None or token_type.lower() != 'bearer':
                return api_abort(400, 'The token type must be bearer.')
            if token is None:
                return token_missing()
            if not validate_token(token):
                return invalid_token()
        return f(*args, **kwargs)

    return decorated
