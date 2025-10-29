
import appdaemon.plugins.hass.hassapi as hass
from plexapi.server import PlexServer
import random

class PlexUpdater(hass.Hass):

    def initialize(self):
        self.log("Plex Updater Initialized")
        self.run_in(self.update_plex_data, 0)
        self.run_daily(self.update_plex_data, "00:00:00")
        self.listen_event(self.get_random_movie, "plex_movie_selector")

    def get_active_plex_clients(self, plex):
        active_clients = []
        try:
            for client in plex.clients():
                if client.isOnline:
                    active_clients.append(client.title)
        except Exception as e:
            self.log(f"Error getting active Plex clients: {e}", level="ERROR")
        return active_clients

    def update_plex_data(self, kwargs):
        self.log("Updating Plex data")
        try:
            plex = PlexServer(self.args["plex_url"], self.args["plex_token"])
            movies_library = plex.library.section('Movies')

            genres = [genre.tag for genre in movies_library.allGenres()]
            decades = sorted(list(set([str(movie.year // 10 * 10) for movie in movies_library.all()])))
            directors = sorted(list(set([director.tag for movie in movies_library.all() for director in movie.directors])))
            actors = sorted(list(set([actor.tag for movie in movies_library.all() for actor in movie.actors])))
            collections = sorted(list(set([collection.tag for movie in movies_library.all() for collection in movie.collections])))
            content_ratings = sorted(list(set([movie.contentRating for movie in movies_library.all() if movie.contentRating])))
            active_clients = self.get_active_plex_clients(plex)

            self.call_service("input_select/set_options", entity_id="input_select.plex_movie_genre", options=genres)
            self.call_service("input_select/set_options", entity_id="input_select.plex_movie_decade", options=decades)
            self.call_service("input_select/set_options", entity_id="input_select.plex_movie_director", options=directors)
            self.call_service("input_select/set_options", entity_id="input_select.plex_movie_actor", options=actors)
            self.call_service("input_select/set_options", entity_id="input_select.plex_movie_collection", options=collections)
            self.call_service("input_select/set_options", entity_id="input_select.plex_movie_content_rating", options=content_ratings)
            self.call_service("input_select/set_options", entity_id="input_select.plex_client_selector", options=active_clients)

            self.log("Plex data updated successfully")

        except Exception as e:
            self.log(f"Error updating Plex data: {e}", level="ERROR")

    def get_random_movie(self, event_name, data, kwargs):
        self.log("Received plex_movie_selector event")
        try:
            plex = PlexServer(self.args["plex_url"], self.args["plex_token"])
            movies_library = plex.library.section('Movies')

            # Get the data from the event
            genre = data.get('genre')
            decade = data.get('decade')
            director = data.get('director')
            actor = data.get('actor')
            use_last_played_actors = data.get('use_last_played_actors')
            collection = data.get('collection')
            content_rating = data.get('content_rating')
            client_name = data.get('client_name')

            # Filter movies by genre and unwatched status
            unwatched_movies = [
                movie for movie in movies_library.search(unwatched=True)
                if genre.lower() in [g.tag.lower() for g in movie.genres]
            ]

            if not unwatched_movies:
                self.log(f"No unwatched movies found in the '{genre}' genre.")
                return

            # Filter movies by decade
            if decade:
                decade = int(decade)
                unwatched_movies = [movie for movie in unwatched_movies if movie.year >= decade and movie.year < decade + 10]

            if not unwatched_movies:
                self.log(f"No unwatched movies found in the '{genre}' genre for the {decade}s.")
                return

            # Filter movies by director
            if director:
                unwatched_movies = [movie for movie in unwatched_movies if director.lower() in [d.tag.lower() for d in movie.directors]]

            if not unwatched_movies:
                self.log(f"No unwatched movies found in the '{genre}' genre for the {decade}s with director '{director}'.")
                return

            # Filter movies by actor
            if actor:
                unwatched_movies = [movie for movie in unwatched_movies if actor.lower() in [a.tag.lower() for a in movie.actors]]

            if not unwatched_movies:
                self.log(f"No unwatched movies found in the '{genre}' genre for the {decade}s with director '{director}' and actor '{actor}'.")
                return

            # Filter by actors from last played movie
            if use_last_played_actors:
                last_played_actors = self.get_actors_from_last_played(plex)
                if last_played_actors:
                    unwatched_movies = [movie for movie in unwatched_movies if any(actor.lower() in [a.tag.lower() for a in movie.actors] for actor in last_played_actors)]

            if not unwatched_movies:
                self.log(f"No unwatched movies found with actors from the last played movie.")
                return

            # Filter by collection
            if collection:
                unwatched_movies = [movie for movie in unwatched_movies if collection.lower() in [c.tag.lower() for c in movie.collections]]

            if not unwatched_movies:
                self.log(f"No unwatched movies found in the '{collection}' collection.")
                return

            # Filter by content rating
            if content_rating:
                unwatched_movies = [movie for movie in unwatched_movies if movie.contentRating.lower() == content_rating.lower()]

            if not unwatched_movies:
                self.log(f"No unwatched movies found with content rating '{content_rating}'.")
                return

            # Group movies by rating
            movie_ratings = {}
            for movie in unwatched_movies:
                rating = movie.rating
                if rating is not None:
                    if rating not in movie_ratings:
                        movie_ratings[rating] = []
                    movie_ratings[rating].append(movie)

            if not movie_ratings:
                self.log("Could not retrieve ratings for any movies.")
                return

            # Select a random movie from the highest-rated group
            highest_rating = max(movie_ratings.keys())
            highest_rated_movies = movie_ratings[highest_rating]
            selected_movie = random.choice(highest_rated_movies)

            # Fire an event back to the python_script
            self.fire_event("plex_movie_selected", movie_title=selected_movie.title, client_name=client_name)

        except Exception as e:
            self.log(f"Error getting random movie: {e}", level="ERROR")

    def get_actors_from_last_played(self, plex):
        """
        Returns a list of actors from the most recently played movie.
        """
        try:
            history = plex.history()
            if history:
                last_played = history[0]
                return [actor.tag for actor in last_played.actors]
        except Exception as e:
            self.log(f"Error getting last played movie: {e}", level="ERROR")
        return []
