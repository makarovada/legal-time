from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/calendar.events'
]

flow = InstalledAppFlow.from_client_secrets_file(
    'credentials.json',
    scopes=SCOPES,
    redirect_uri='http://localhost:8080'  # явно укажем, чтобы быть уверенным
)

# ВЫВЕДЕМ точный authorization url
auth_url, _ = flow.authorization_url(prompt='consent')
print("Перейдите по этой ссылке вручную, если браузер не открылся:")
print(auth_url)

creds = flow.run_local_server(port=8080, bind_address='127.0.0.1')
print("Успех!")