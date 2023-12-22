import os
import dotenv
import requests


dotenv.load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
APIS = {
    "domain": "https://ws.rcc.fsu.edu",
    "auth_subpath": "/auth",
    "people_subpath": "people?canSponsor=true&page[limit]=9999&fields[people]=firstName,lastName,employeeId",
}


def get_token():
    payload = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }

    response = requests.post(
        f'{APIS.get("domain")}{APIS.get("auth_subpath")}', json=payload
    )

    if response.status_code != requests.codes.ok:
        raise Exception("Error: Could not authenticate!")

    return response.json()


# TODO: 2. Get people list.
# TODO: 3. Read grants excel.
# TODO: 4. Keep rows which we are interested in.
# TODO: 5. Make entries for grant_award table. (If get all is done, mark the unpaired awards as inactive)
# TODO: 6. Make entries for the grant_award table.
# TODO: 7. Write the data.


def main():
    if CLIENT_ID is None or CLIENT_SECRET is None:
        raise Exception(
            "Error: .env file must be contain CLIENT_ID and CLIENT_SECRET information."
        )

    token = get_token()


if __name__ == "__main__":
    main()
