from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)


@app.route('/')
@app.route('/restaurants')
def showRestaurants():
    return("show restaurants")


@app.route('/restaurant/new')
def newRestaurant():
    return ("new restaurant")


@app.route('/restaurant/<int:restaurant_id>/edit')
def editRestaurant():
    return ("edit restaurant")


@app.route('/restaurant/<int:restaurant_id>/delete')
def editRestaurant():
    return ("delete restaurant")


@app.route('/restaurant/<int:restaurant_id>')
@app.route('/restaurant/<int:restaurant_id>/menu')
def showMenu():
    return ("restaurant menu")


@app.route('/restaurant/<int:restaurant_id>/new')
def newMenuItem():
    return ("new menu item")


@app.route('/restaurant/<int:restaurant_id>/edit')
def editMenuItem():
    return ("edit menu item")


@app.route('/restaurant/<int:restaurant_id>/delete')
def deleteMenuItem():
    return ("delete menu item")
