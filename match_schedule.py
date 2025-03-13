import requests
import json
import os

# Define the API endpoint and your event key
api_url = "https://www.thebluealliance.com/api/v3"
event_key = "2025inmis"
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

# Function to extract all six teams (Red & Blue alliances) in the required format
def extract_all_teams(matches):
    match_data = {}

    # Separate qualification matches and playoff matches
    qual_matches = [m for m in matches if m.get('comp_level') == 'qm']
    playoff_matches = [m for m in matches if m.get('comp_level') != 'qm']

    # Process qualification match 1 first
    if qual_matches:
        first_match = min(qual_matches, key=lambda m: m.get('match_number', float('inf')))
        match_number = first_match.get('match_number')

        red_teams = first_match.get('alliances', {}).get('red', {}).get('team_keys', [])
        blue_teams = first_match.get('alliances', {}).get('blue', {}).get('team_keys', [])

        teams = [{"number": team[3:], "color": "red"} for team in red_teams if team.startswith("frc")] + \
                [{"number": team[3:], "color": "blue"} for team in blue_teams if team.startswith("frc")]

        match_data[str(match_number)] = {
            "match_number": str(match_number),
            "teams": teams
        }

        # Remove the first qualification match from the list
        qual_matches = [m for m in qual_matches if m != first_match]

    # Process the remaining matches
    sorted_matches = sorted(qual_matches + playoff_matches, key=lambda m: m.get('match_number', 0))

    for match in sorted_matches:
        match_number = match.get('match_number')
        if match_number is None or str(match_number) in match_data:
            continue  # Skip duplicate match numbers

        red_teams = match.get('alliances', {}).get('red', {}).get('team_keys', [])
        blue_teams = match.get('alliances', {}).get('blue', {}).get('team_keys', [])

        teams = [{"number": team[3:], "color": "red"} for team in red_teams if team.startswith("frc")] + \
                [{"number": team[3:], "color": "blue"} for team in blue_teams if team.startswith("frc")]

        match_data[str(match_number)] = {
            "match_number": str(match_number),
            "teams": teams
        }

    return match_data  # Return dictionary with match numbers as keys

# Function to save match data to JSON
def save_matches_to_file(matches_data, filename="match_schedule.json"):
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
        all_teams_data = extract_all_teams(matches)
        save_matches_to_file(all_teams_data)  # Saves to "Matches.json"

if __name__ == "__main__":
    main()
