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

# Function to extract all red alliance teams
def extract_red_alliance(matches):
    red_matches = {}

    # Separate qualification matches and playoff matches
    qual_matches = [m for m in matches if m.get('comp_level') == 'qm']
    playoff_matches = [m for m in matches if m.get('comp_level') != 'qm']

    # Ensure qualification match 1 is first
    if qual_matches:
        first_qual_match = min(qual_matches, key=lambda m: m.get('match_number', float('inf')))
        match_number = first_qual_match.get('match_number')

        red_teams = first_qual_match.get('alliances', {}).get('red', {}).get('team_keys', [])
        teams = [{"number": team[3:], "color": "red"} for team in red_teams if team.startswith("frc")]

        red_matches[str(match_number)] = {
            "match_number": str(match_number),
            "teams": teams
        }

    # Process the rest of the matches normally
    sorted_matches = sorted(qual_matches + playoff_matches, key=lambda m: m.get('match_number', 0))
    for match in sorted_matches:
        match_number = match.get('match_number')
        if match_number is None or str(match_number) in red_matches:
            continue  # Skip qual match 1 since it's already added

        red_teams = match.get('alliances', {}).get('red', {}).get('team_keys', [])
        teams = [{"number": team[3:], "color": "red"} for team in red_teams if team.startswith("frc")]

        red_matches[str(match_number)] = {
            "match_number": str(match_number),
            "teams": teams
        }

    return {"Red": red_matches}  # Wrap in "Red" key

# Function to save red alliance data to RedSub.JSON
def save_matches_to_file(matches_data, filename="RedSub.json"):
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
        red_alliance_data = extract_red_alliance(matches)
        save_matches_to_file(red_alliance_data)  # Saves to "RedSub.json"

if __name__ == "__main__":
    main()
