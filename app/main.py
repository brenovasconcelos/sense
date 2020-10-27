from flask import Flask, render_template, request

import requests

import ast

app = Flask(__name__)


@app.route("/")
def hello():
    return render_template("base.html")


@app.route("/get-data")
def get_characters():

    page = request.args.get("page")
    if page:
        ret = requests.get(page).json()
    else:
        ret = requests.get("https://swapi.dev/api/people/").json()

    ret["results"] = [
        {
            k: v
            for k, v in item.items()
            if k
            not in [
                "species",
                "created",
                "edited",
                "url",
            ]
        }
        for item in ret["results"]
    ]
    films = requests.get("https://swapi.dev/api/films/").json()
    films = {film["episode_id"]: film for film in films["results"]}
    starships = get_starships()
    starships_dict = get_starships_dict(starships)

    planets = get_planets()
    planets_dict = get_planets_dict(planets)

    vehicles = get_vehicles()
    vehicles_dict = get_vehicles_dict(vehicles)
    for char in ret["results"]:

        if char["mass"] != "unknown":
            char["mass"] = char["mass"].replace(",", ".")
            char["mass"] = float(char["mass"])
        if char["height"] != "unknown":
            char["height"] = float(char["height"])

        films_list = []
        for film in char["films"]:
            episode_id = int(film.split("/")[-2])
            films_list.append(films[episode_id]["title"])
        starships_list = []
        for starship in char["starships"]:
            starship_id = int(starship.split("/")[-2])
            starships_list.append(starships_dict[starship_id]["name"])

        vehicles_list = []
        for vehicle in char["vehicles"]:
            vehicle_id = int(vehicle.split("/")[-2])
            vehicles_list.append(vehicles_dict[vehicle_id]["name"])

        planet_id = int(char["homeworld"].split("/")[-2])
        char["homeworld"] = planets_dict[planet_id]["name"]
        char["vehicles"] = vehicles_list
        char["films"] = films_list
        char["starships"] = starships_list

    ret["all_films"] = films
    ret["all_starships"] = starships_dict
    ret["all_planets"] = planets_dict
    ret["all_vehicles"] = vehicles_dict
    return render_template("pagination.html", char_list=ret)


def get_starships_dict(starships):

    starships_clean = {}
    for starship in starships:
        starship_id = int(starship["url"].split("/")[-2])
        starships_clean[starship_id] = starship
    return starships_clean


def get_planets_dict(planets):

    planets_clean = {}
    for planet in planets:
        planet_id = int(planet["url"].split("/")[-2])
        planets_clean[planet_id] = planet
    return planets_clean


def get_vehicles_dict(vehicles):

    vehicles_clean = {}
    for vehicle in vehicles:
        vehicle_id = int(vehicle["url"].split("/")[-2])
        vehicles_clean[vehicle_id] = vehicle
    return vehicles_clean


@app.route("/filter")
def filter_by():
    reverse = False
    char_list = ast.literal_eval(request.args.get("char_list"))
    char_attribute = request.args.get("char_attribute")
    if char_attribute in ["mass", "height"]:
        reverse = True
    clean_to_sort = []
    unknow_list = []

    for item in char_list["results"]:
        if item[char_attribute] == "unknown":
            unknow_list.append(item)
            continue
        clean_to_sort.append(item)

    char_list["results"] = sorted(
        clean_to_sort, key=lambda x: x[char_attribute], reverse=reverse
    )
    char_list["results"] += unknow_list
    return render_template("pagination.html", char_list=char_list)


@app.route("/film_filter")
def film_filter():
    char_list = ast.literal_eval(request.args.get("char_list"))
    film_filter = request.args.get("film_filter")
    char_list_films = [
        char for char in char_list["results"] if film_filter in char["films"]
    ]
    char_list["results"] = char_list_films
    return render_template("pagination.html", char_list=char_list)


@app.route("/starship_filter")
def starship_filter():
    char_list = ast.literal_eval(request.args.get("char_list"))
    starship_filter = request.args.get("starship_filter")
    char_list_starships = [
        char for char in char_list["results"] if starship_filter in char["starships"]
    ]
    char_list["results"] = char_list_starships
    return render_template("pagination.html", char_list=char_list)


@app.route("/vehicle_filter")
def vehicle_filter():
    char_list = ast.literal_eval(request.args.get("char_list"))
    vehicle_filter = request.args.get("vehicle_filter")
    char_list_vechicles = [
        char for char in char_list["results"] if vehicle_filter in char["vehicles"]
    ]
    char_list["results"] = char_list_vechicles
    return render_template("pagination.html", char_list=char_list)


@app.route("/planets_filter")
def planets_filter():
    char_list = ast.literal_eval(request.args.get("char_list"))
    planets_filter = request.args.get("planets_filter")
    char_list_planets = [
        char for char in char_list["results"] if planets_filter in char["homeworld"]
    ]
    char_list["results"] = char_list_planets
    return render_template("pagination.html", char_list=char_list)


@app.route("/starships")
def starships():

    starships_clean = get_starships()

    for starship in starships_clean:
        if (
            starship["hyperdrive_rating"] != "unknown"
            and starship["cost_in_credits"] != "unknown"
        ):
            hr = float(starship["hyperdrive_rating"])
            cic = float(starship["cost_in_credits"])
            score = hr / cic
            starship["score"] = score
        else:
            starship["score"] = 0
    return render_template(
        "starships.html",
        starships=sorted(starships_clean, key=lambda x: x["score"], reverse=True),
    )


def get_starships():
    starships = []
    url = "https://swapi.dev/api/starships/"
    stop = False
    while not stop:
        starships_response = requests.get(url).json()
        starships += starships_response["results"]
        if starships_response["next"]:
            url = starships_response["next"]
        else:
            stop = True

    starships_clean = [
        {
            k: v
            for k, v in item.items()
            if k
            not in [
                "films",
                "created",
                "pilots",
                "edited",
            ]
        }
        for item in starships
    ]

    return starships_clean


def get_planets():
    planets = []
    url = "https://swapi.dev/api/planets/"
    stop = False
    while not stop:
        planets_response = requests.get(url).json()
        planets += planets_response["results"]
        if planets_response["next"]:
            url = planets_response["next"]
        else:
            stop = True

    return planets


def get_vehicles():
    planets = []
    url = "https://swapi.dev/api/vehicles/"
    stop = False
    while not stop:
        planets_response = requests.get(url).json()
        planets += planets_response["results"]
        if planets_response["next"]:
            url = planets_response["next"]
        else:
            stop = True

    return planets


if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host="0.0.0.0", debug=True, port=80)