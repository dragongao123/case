# -*- coding: utf-8 -*-

from flask.ext.pymongo import PyMongo
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext import admin

__all__ = ['mongo', 'db', 'admin']

db = SQLAlchemy()
mongo = PyMongo()
admin = admin.Admin(name=u'系统 数据库管理')
