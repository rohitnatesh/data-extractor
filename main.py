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


def get_all_rcc_people(token):
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
            "employeeId": person["attributes"]["employeeId"],
        }
        for person in response["data"]
    ]

    return pd.DataFrame(data)


def filter_grants(row, all_rcc_people_df):
    pi_employee_id = row["Person Id"]
    match_row = all_rcc_people_df[all_rcc_people_df["employeeId"] == pi_employee_id]

    if not match_row.empty:
        row["json"] = row.to_json()
        (
            row["matchedId"],
            row["matchedFirstName"],
            row["matchedLastName"],
            row["matchedEmployeeId"],
        ) = match_row.values[0]

        return row

    co_pi_list = str(row["Co-PI  Emplid Name List"]).split(";")

    for co_pi in co_pi_list:
        co_pi_employee_id = co_pi.split(" - ")[0]
        match_row = all_rcc_people_df[
            all_rcc_people_df["employeeId"] == co_pi_employee_id
        ]

        if not match_row.empty:
            row["json"] = row.to_json()
            (
                row["matchedId"],
                row["matchedFirstName"],
                row["matchedLastName"],
                row["matchedEmployeeId"],
            ) = match_row.values[0]

            return row

    return pd.Series()


def get_rcc_grants(all_rcc_people_df, grants_df):
    rcc_grants = grants_df.apply(
        lambda row: filter_grants(row, all_rcc_people_df), axis=1
    )

    return rcc_grants.dropna()


# TODO: 5. Make entries for grant_award table. (If get all is done, mark the unpaired awards as inactive)
# TODO: 6. Make entries for the grant_award table.
# TODO: 7. Write the data.


def main():
    grants_df = pd.read_excel(sys.argv[1])
    grants_df["Person Id"] = grants_df["Person Id"].apply(
        lambda entry: str(entry).zfill(9)
    )

    token = get_token()
    all_rcc_people_df = get_all_rcc_people(token)
    rcc_grants_df = get_rcc_grants(all_rcc_people_df, grants_df)


if __name__ == "__main__":
    if CLIENT_ID is None or CLIENT_SECRET is None:
        raise Exception(
            ".env file must be contain CLIENT_ID and CLIENT_SECRET information."
        )

    if len(sys.argv) < 2:
        raise Exception(
            "Invalid usage! Path to the Grants Excel should be passed as argument."
        )

    main()
