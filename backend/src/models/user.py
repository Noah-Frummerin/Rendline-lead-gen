{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fnil\fcharset0 Menlo-Regular;}
{\colortbl;\red255\green255\blue255;\red77\green80\blue85;\red236\green241\blue247;\red0\green0\blue0;
\red111\green14\blue195;\red24\green112\blue43;\red164\green69\blue11;}
{\*\expandedcolortbl;;\cssrgb\c37255\c38824\c40784;\cssrgb\c94118\c95686\c97647;\cssrgb\c0\c0\c0;
\cssrgb\c51765\c18824\c80784;\cssrgb\c9412\c50196\c21961;\cssrgb\c70980\c34902\c3137;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\deftab720
\pard\pardeftab720\partightenfactor0

\f0\fs28 \cf2 \cb3 \expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 # This file defines the database and the User model.\cf0 \cb1 \strokec4 \
\pard\pardeftab720\partightenfactor0
\cf5 \cb3 \strokec5 from\cf0 \strokec4  flask_sqlalchemy \cf5 \strokec5 import\cf0 \strokec4  SQLAlchemy\cb1 \
\
\pard\pardeftab720\partightenfactor0
\cf2 \cb3 \strokec2 # Initialize the SQLAlchemy database object\cf0 \cb1 \strokec4 \
\pard\pardeftab720\partightenfactor0
\cf0 \cb3 db = SQLAlchemy()\cb1 \
\
\pard\pardeftab720\partightenfactor0
\cf5 \cb3 \strokec5 class\cf0 \strokec4  User(db.Model):\cb1 \
\pard\pardeftab720\partightenfactor0
\cf0 \cb3     __tablename__ = \cf6 \strokec6 'user'\cf0 \cb1 \strokec4 \
\cb3     \cf5 \strokec5 id\cf0 \strokec4  = db.Column(db.Integer, primary_key=\cf5 \strokec5 True\cf0 \strokec4 )\cb1 \
\cb3     username = db.Column(db.String(\cf7 \strokec7 80\cf0 \strokec4 ), unique=\cf5 \strokec5 True\cf0 \strokec4 , nullable=\cf5 \strokec5 False\cf0 \strokec4 )\cb1 \
\cb3     email = db.Column(db.String(\cf7 \strokec7 120\cf0 \strokec4 ), unique=\cf5 \strokec5 True\cf0 \strokec4 , nullable=\cf5 \strokec5 False\cf0 \strokec4 )\cb1 \
\
\cb3     \cf5 \strokec5 def\cf0 \strokec4  __repr__(\cf5 \strokec5 self\cf0 \strokec4 ):\cb1 \
\cb3         \cf5 \strokec5 return\cf0 \strokec4  \cf6 \strokec6 '<User %r>'\cf0 \strokec4  % \cf5 \strokec5 self\cf0 \strokec4 .username\cb1 \
\
}