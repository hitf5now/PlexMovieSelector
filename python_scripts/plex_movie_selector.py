

# Get the data from the script call
genre = data.get('genre')
decade = data.get('decade')
director = data.get('director')
actor = data.get('actor')
use_last_played_actors = data.get('use_last_played_actors')
collection = data.get('collection')
content_rating = data.get('content_rating')
client_name = data.get('client_name')

# Fire an event to the AppDaemon app
hass.bus.fire('plex_movie_selector', {
    'genre': genre,
    'decade': decade,
    'director': director,
    'actor': actor,
    'use_last_played_actors': use_last_played_actors,
    'collection': collection,
    'content_rating': content_rating,
    'client_name': client_name
})

def play_movie(event):
    movie_title = event.data.get('movie_title')
    client_name = event.data.get('client_name')
    hass.services.call('media_player', 'play_media', {
        'entity_id': f"media_player.{client_name}",
        'media_content_id': f'plex://{movie_title}',
        'media_content_type': 'movie'
    }, False)

hass.bus.listen("plex_movie_selected", play_movie)
