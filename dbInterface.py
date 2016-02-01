#!/usr/bin/python
# coding: utf8
# 19-01-16 EMaulandi
#TODO : stocker nom DB ailleurs que en dur !
# Interface with the SQLITE3 database

from recipe import Recipe
import sqlite3

# === Begin : Constants definition ==============
#SET YOUR DATABASE NAME HERE
DATABASE_NAME = '/home/cmoron/devv/RandomFood/db/development.sqlite3'

##Database fields
ID_FIELD_NAME = "id"
RECIPE_TABLE_NAME = 'recipes'
RECIPE_ID_NAME = 'recipe_id'
RECIPE_NAME_NAME = 'name'

INGREDIENTS_TABLE_NAME = 'ingredients'
INGREDIENT_ID_NAME = 'ingredient_id'
INGREDIENT_NAME_NAME = 'name'

JOINT_TABLE_NAME = 'links'
CREATED_AT_FIELD_NAME = 'created_at'
UPDATED_AT_FIELD_NAME = 'updated_at'
# === End : Constants definition ================

# === Begin : Global variable definition ========
slite_connexion = sqlite3.connect(DATABASE_NAME)
slite_cursor = slite_connexion.cursor()
# === End : Global variables definition =========

# This method return the primary key of an ingredient in the ingredients table
def getKeyIngredient(ingredient):
    slite_connexion.commit()
    slite_cursor = slite_connexion.cursor()
    sql2 = "select %s from %s where %s='%s';"%(ID_FIELD_NAME, INGREDIENTS_TABLE_NAME, INGREDIENT_NAME_NAME, ingredient)
    slite_cursor.execute(sql2)
    results = slite_cursor.fetchall()
    if len(results)>0:
        if len(results[0])>0:
            result = (results[0][0])
            return result;
        else:
            print("The ingredient seems not to be in the data base")
    else:
        print("The ingredient seems not to be in the data base")

#This method return the primary key of an recipe in the recipes table
def getKeyRecipe(recipe):
    slite_connexion.commit()
    slite_cursor = slite_connexion.cursor()
    sql2 = "select %s from %s where %s='%s';"%(ID_FIELD_NAME, RECIPE_TABLE_NAME, RECIPE_NAME_NAME, recipe)
    slite_cursor.execute(sql2)
    results = slite_cursor.fetchall()
    if len(results)>0:
        if len(results[0])>0:
            result = (results[0][0])
            return result;
        else:
            print("The recipe seems not to be in the data base")
    else:
        print("The recipe seems not to be in the data base")

#The random_food database manager
class RandomFoodDataBase: 

    #constructor (builds 3 empty tables)
    #Warning: an error is raised if the tables already exists. The initDB.py script can be used in this case.
    def __init__(self):
        slite_cursor = slite_connexion.cursor()

        #slite_cursor.execute("""DROP TABLE if exists %s;"""%RECIPE_TABLE_NAME);
        #slite_cursor.execute("""DROP TABLE if exists %s;"""%INGREDIENTS_TABLE_NAME);
        #slite_cursor.execute("""DROP TABLE if exists %s;"""%JOINT_TABLE_NAME);

        slite_cursor.execute("""CREATE TABLE if not exists
            %s(%s INTEGER PRIMARY KEY,
            %s varchar(300) UNIQUE NOT NULL,
            %s datetime NOT NULL,
            %s datetime NOT NULL)"""
            %(RECIPE_TABLE_NAME,
                ID_FIELD_NAME,
                RECIPE_NAME_NAME,
                CREATED_AT_FIELD_NAME,
                UPDATED_AT_FIELD_NAME))

        slite_cursor.execute("""CREATE TABLE if not exists
            %s(%s INTEGER PRIMARY KEY,
            %s varchar(50) UNIQUE NOT NULL,
            %s datetime NOT NULL,
            %s datetime NOT NULL);"""
            %(INGREDIENTS_TABLE_NAME,
                ID_FIELD_NAME,
                INGREDIENT_NAME_NAME,
                CREATED_AT_FIELD_NAME,
                UPDATED_AT_FIELD_NAME))

        slite_cursor.execute("""CREATE TABLE if not exists 
            %s(%s INTEGER PRIMARY KEY,
            %s INTEGER,
            %s INTEGER,
            %s datetime NOT NULL,
            %s datetime NOT NULL);"""
            %(JOINT_TABLE_NAME,
                ID_FIELD_NAME,
                RECIPE_ID_NAME,
                INGREDIENT_ID_NAME,
                CREATED_AT_FIELD_NAME,
                UPDATED_AT_FIELD_NAME))

        print("random_food database created")


    #Method for adding a recipe. Take a Recipe object in argument.
    def addRecipe(self, recipe):
        print("add recipe")
        recipeName = recipe.name.replace(u"'",u" ")#the apostrophe raises error in mysql syntax.
        #TODO find a way to keep the correct name of the recipe...
        recipeName = recipeName.replace(u"é",u"e")#The accent raises error in mysql syntax.
        try:
            #test si recette existe dejà
                slite_cursor = slite_connexion.cursor()
                slite_cursor.execute("SELECT * FROM %s WHERE %s = '%s';"%(RECIPE_TABLE_NAME,RECIPE_NAME_NAME,recipeName))
                exist = slite_cursor.fetchone()
                if exist == None:
                    slite_cursor.execute(u"""INSERT INTO %s VALUES (NULL, '%s', datetime(), datetime());"""%(RECIPE_TABLE_NAME,recipeName))
                    print("New recipe added to the database:")
                    nbIngredients = len(recipe.ingredients)
                    recipeId = getKeyRecipe(recipeName)
                    print(RECIPE_ID_NAME)
                    print("recipe id:"+str(RECIPE_ID_NAME))
                    #Iteration on all ingredients to add them in the db.
                    for i in range(nbIngredients) :
                        try:
                            ingredientName = recipe.ingredients[i];
                            #test si ingredient existe dejà
                            slite_cursor = slite_connexion.cursor()
                            slite_cursor.execute("SELECT * FROM %s WHERE %s = '%s';"%(INGREDIENTS_TABLE_NAME,INGREDIENT_NAME_NAME,ingredientName))
                            exist = slite_cursor.fetchone()
                            if exist == None:
                                slite_cursor.execute("""INSERT INTO %s VALUES (NULL, '%s', datetime(), datetime());"""%(INGREDIENTS_TABLE_NAME,ingredientName))
                                print("ingredient ajoute: "+str(ingredientName))
                            else:
                                print("ingredient deja existant: "+str(ingredientName))
                        except sqlite3.IntegrityError:
                            pass

                        slite_connexion.commit()
                        ingredientId = getKeyIngredient(ingredientName)
                        print(INGREDIENT_ID_NAME)
                        try:
                            #Complete the junction table (matches recipe with ingredient key biatch)
                            slite_cursor.execute("INSERT INTO %s VALUES (NULL, %d,%d, datetime(), datetime())"%(JOINT_TABLE_NAME,recipeId,ingredientId))
                        except sqlite3.IntegrityError:
                            pass
                else:
                    print("Recipe Already exists")
        except sqlite3.Error as e:
            print "Error %s" % (e.args[0])


    def closeDB():
        slite_connexion.close()

