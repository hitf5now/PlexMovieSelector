# Project Overview

This project provides a "Plex Movie Night" feature for Home Assistant. It allows users to select a random movie from their Plex library based on genre, decade, director, actor, collection, and content rating. It can also suggest movies based on the actors in the last played movie. The selection is then played on a chosen active Plex client.

This functionality is implemented using an AppDaemon app that interacts with the Plex API and Home Assistant's `input_select` and `input_boolean` helpers. A Home Assistant Python script acts as an intermediary to trigger the AppDaemon app and initiate movie playback.

# Installation (HACS)

This project is designed to be installed via the Home Assistant Community Store (HACS) as a custom repository.

1.  **Add Custom Repository to HACS:**
    *   In Home Assistant, navigate to HACS.
    *   Go to <strong>Integrations</strong>.
    *   Click the three dots in the top right corner and select <strong>Custom repositories</strong>.
    *   Add the URL of this Git repository (where these files are hosted) as a new repository.
        *   <strong>Repository URL</strong>: `[YOUR_REPOSITORY_URL]` (e.g., `https://github.com/your_username/plex-movie-selector`)
        *   <strong>Category</strong>: Select `AppDaemon`
2.  **Install from HACS:**
    *   Close the custom repositories dialog.
    *   Search for "Plex Movie Selector" in HACS and install it.
    *   HACS will place the AppDaemon app (`plex_updater.py`) and the Home Assistant Python script (`plex_movie_selector.py`) in their correct locations.
3.  **Configure AppDaemon (`appdaemon/apps/apps.yaml`):**
    *   Edit the `apps.yaml` file (typically located in your AppDaemon's `apps` directory, e.g., `/config/appdaemon/apps/apps.yaml`).
    *   Add the following configuration, replacing placeholders with your Plex server details:
        ```yaml
        plex_updater:
          module: plex_updater
          class: PlexUpdater
          plex_url: YOUR_PLEX_URL
          plex_token: YOUR_PLEX_TOKEN
        ```
4.  **Home Assistant Configuration (`configuration.yaml`):**
    *   Ensure your Home Assistant `configuration.yaml` includes the necessary lines for scripts, automations, and python_scripts. If you don't have them, add these lines:
        ```yaml
        script: !include scripts.yaml
        automation: !include automations.yaml
        python_script:
        ```
5.  **Home Assistant Automation (`automations.yaml`):**
    *   Add the following automation to your `automations.yaml` file:
        ```yaml
        automation:
          - alias: "Plex Movie Night"
            trigger:
              - platform: state
                entity_id: input_button.plex_movie_night_button
            action:
              - service: script.plex_movie_night
        ```
6.  **Home Assistant Script (`scripts.yaml`):**
    *   Add the following script to your `scripts.yaml` file:
        ```yaml
        plex_movie_night:
          alias: Plex Movie Night
          sequence:
            - service: python_script.plex_movie_selector
              data_template:
                genre: "{{ states('input_select.plex_movie_genre') }}"
                decade: "{{ states('input_select.plex_movie_decade') }}"
                director: "{{ states('input_select.plex_movie_director') }}"
                actor: "{{ states('input_select.plex_movie_actor') }}"
                use_last_played_actors: "{{ states('input_boolean.plex_use_last_played_actors') }}"
                collection: "{{ states('input_select.plex_movie_collection') }}"
                content_rating: "{{ states('input_select.plex_movie_content_rating') }}"
                client_name: "{{ states('input_select.plex_client_selector') }}"
        ```
7.  **Create Home Assistant Helpers:**
    *   Via <strong>Configuration -> Helpers -> + Add Helper</strong>, create the following:
        *   <strong>Button</strong>: `Plex Movie Night Button` (<code>input_button.plex_movie_night_button</code>).
        *   <strong>Dropdown</strong>: `Plex Movie Genre` (<code>input_select.plex_movie_genre</code>).
        *   <strong>Dropdown</strong>: `Plex Movie Decade` (<code>input_select.plex_movie_decade</code>).
        *   <strong>Dropdown</strong>: `Plex Movie Director` (<code>input_select.plex_movie_director</code>).
        *   <strong>Dropdown</strong>: `Plex Movie Actor` (<code>input_select.plex_movie_actor</code>).
        *   <strong>Toggle</strong>: `Plex Use Last Played Actors` (<code>input_boolean.plex_use_last_played_actors</code>).
        *   <strong>Dropdown</strong>: `Plex Movie Collection` (<code>input_select.plex_movie_collection</code>).
        *   <strong>Dropdown</strong>: `Plex Movie Content Rating` (<code>input_select.plex_movie_content_rating</code>).
        *   <strong>Dropdown</strong>: `Plex Client Selector` (<code>input_select.plex_client_selector</code>).
        *(Note: Dropdown options will be populated by the AppDaemon app.)*
8.  **Install Python Dependencies (for AppDaemon):**
    *   Access the terminal for your AppDaemon environment and run: `pip install plexapi`
9.  **Restart Services:**
    *   Restart your AppDaemon addon/service.
    *   Restart your Home Assistant instance.

# Development Conventions

The project utilizes an AppDaemon app for core logic and dynamic data population, a Home Assistant Python script as an intermediary, and standard Home Assistant YAML configurations for automations and scripts. This modular approach allows for flexible filtering and interaction with Plex and Home Assistant.