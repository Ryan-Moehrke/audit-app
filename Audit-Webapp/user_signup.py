

def app():
    import google_api_python_client
    
    # Create a state token to prevent request forgery.
    # Store it in the session for later validation.
    state = hashlib.sha256(os.urandom(1024)).hexdigest()
    session['state'] = state
    # Set the client ID, token state, and application name in the HTML while
    # serving it.
    response = make_response(
        render_template('index.html',
                        CLIENT_ID=CLIENT_ID,
                        STATE=state,
                        APPLICATION_NAME=APPLICATION_NAME))

    # Ensure that the request is not a forgery and that the user sending
    # this connect request is the expected user.
    if request.args.get('state', '') != session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
  
def app2():
    import google.oauth2.credentials
    import google_auth_oauthlib.flow

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'path_to_directory/client_secret.json',
        scopes=['https://www.googleapis.com/auth/calendar'])

    flow.redirect_uri = 'https://www.example.com/oauth2callback'

app()
