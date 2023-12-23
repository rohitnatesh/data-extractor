import os
import sys
import dotenv
import requests
import pandas as pd


dotenv.load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
APIS = {
    "domain": "https://ws.rcc.fsu.edu",
    "auth_subpath": "/auth",
    "people_subpath": "/people?canSponsor=true&page[limit]=9999&fields[people]=firstName,lastName,employeeId",
}


def get_token():
    url = f'{APIS["domain"]}{APIS["auth_subpath"]}'
    payload = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    response = requests.post(url, json=payload)

    if response.status_code != requests.codes.ok:
        raise Exception(
            f"\nError: Request failed: {url}\nHTTP status: {response.status_code}"
        )

    return response.json()


def get_all_people(token):
    url = f'{APIS["domain"]}{APIS["people_subpath"]}'
    headers = {"Authorization": f'{token["token_type"]} {token["access_token"]}'}
    response = requests.get(url, headers=headers)

    if response.status_code != requests.codes.ok:
        raise Exception(f"\nRequest failed: {url}\nHTTP Status: {response.status_code}")

    response = response.json()

    data = [
        {
            "id": person["id"],
            "firstName": person["attributes"]["firstName"],
            "lastName": person["attributes"]["lastName"],
        }
        for person in response["data"]
    ]

    return pd.DataFrame(data)

# TODO: 4. Keep rows which we are interested in.
# TODO: 5. Make entries for grant_award table. (If get all is done, mark the unpaired awards as inactive)
# TODO: 6. Make entries for the grant_award table.
# TODO: 7. Write the data.


def main():
    if CLIENT_ID is None or CLIENT_SECRET is None:
        raise Exception(
            ".env file must be contain CLIENT_ID and CLIENT_SECRET information."
        )
    
    if(len(sys.argv) < 2):
        raise Exception("Invalid usage! Path to the Grants Excel should be passed as argument.")

    grants_df = pd.read_excel(sys.argv[1])
    
    token = get_token()
    all_people_df = get_all_people(token)


if __name__ == "__main__":
    main()
