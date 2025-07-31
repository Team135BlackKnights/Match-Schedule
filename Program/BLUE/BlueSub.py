import requests
import json
import os

# Define the API endpoint and your event key
api_url = "https://www.thebluealliance.com/api/v3"
event_key = "enter_id_here"
auth_key = "LPBFcLNYuYkJhRemUEfXyXNCz8qLHLyIGO7LtKQHY25vzayHqelEodBQdZeJCFrq"

# Define the headers with your authentication key
headers = {
    "X-TBA-Auth-Key": auth_key
}

# Function to get match schedule
def get_match_schedule(event_key):
    response = requests.get(f"{api_url}/event/{event_key}/matches", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve matches: {response.status_code}")
        return None

# Function to extract all blue alliance teams ensuring qual match 1 is first
def extract_blue_alliance(matches):
    blue_matches = {}

    # Separate qualification matches and playoff matches
    qual_matches = [m for m in matches if m.get('comp_level') == 'qm']
    playoff_matches = [m for m in matches if m.get('comp_level') != 'qm']

    # Ensure qualification match 1 is first
    if qual_matches:
        first_qual_match = min(qual_matches, key=lambda m: m.get('match_number', float('inf')))
        match_number = first_qual_match.get('match_number')

        blue_teams = first_qual_match.get('alliances', {}).get('blue', {}).get('team_keys', [])
        teams = [{"number": team[3:], "color": "blue"} for team in blue_teams if team.startswith("frc")]

        blue_matches[str(match_number)] = {
            "match_number": str(match_number),
            "teams": teams
        }

    # Process the rest of the matches normally
    sorted_matches = sorted(qual_matches + playoff_matches, key=lambda m: m.get('match_number', 0))
    for match in sorted_matches:
        match_number = match.get('match_number')
        if match_number is None or str(match_number) in blue_matches:
            continue  # Skip qual match 1 since it's already added

        blue_teams = match.get('alliances', {}).get('blue', {}).get('team_keys', [])
        teams = [{"number": team[3:], "color": "blue"} for team in blue_teams if team.startswith("frc")]

        blue_matches[str(match_number)] = {
            "match_number": str(match_number),
            "teams": teams
        }

    return {"Blue": blue_matches}  # Wrap in "Blue" key

# Function to save blue alliance data to BlueSub.JSON
def save_matches_to_file(matches_data, filename="BlueSub.json"):
    try:
        file_path = os.path.join(os.getcwd(), filename)  # Save in current directory
        with open(file_path, "w") as file:
            json.dump(matches_data, file, indent=4)
        print(f"Data saved to {file_path}")
    except Exception as e:
        print("Error saving data:", e)

# Main function
def main():
    matches = get_match_schedule(event_key)
    if matches:
        blue_alliance_data = extract_blue_alliance(matches)
        save_matches_to_file(blue_alliance_data)  # Saves to "BlueSub.json"

if __name__ == "__main__":
    main()
