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

# Function to extract only the SECOND blue alliance team
def extract_second_blue_team(matches):
    blue_matches = {}
    sorted_matches = sorted(matches, key=lambda m: (m.get('comp_level', ''), m.get('match_number', 0)))
    
    # Find the first qualification match
    first_qual_match = next((m for m in sorted_matches if m.get('comp_level') == 'qm'), None)
    if first_qual_match:
        match_number = first_qual_match.get('match_number')
        blue_teams = first_qual_match.get('alliances', {}).get('blue', {}).get('team_keys', [])
        
        if len(blue_teams) >= 2:
            second_blue_team = blue_teams[1][3:] if blue_teams[1].startswith("frc") else blue_teams[1]
            blue_matches[str(match_number)] = {
                "match_number": str(match_number),
                "team": {"number": second_blue_team, "color": "blue"}
            }
    
    # Process the rest of the matches
    for match in sorted_matches:
        match_number = match.get('match_number')
        if match_number is None or str(match_number) in blue_matches:
            continue

        blue_teams = match.get('alliances', {}).get('blue', {}).get('team_keys', [])
        
        if len(blue_teams) >= 2:
            second_blue_team = blue_teams[1][3:] if blue_teams[1].startswith("frc") else blue_teams[1]
            blue_matches[str(match_number)] = {
                "match_number": str(match_number),
                "team": {"number": second_blue_team, "color": "blue"}
            }

    return {"Blue 2": blue_matches}  # Wrap in "Blue 2" key

# Function to save blue alliance data to a JSON file
def save_matches_to_file(matches_data, filename="BlueTwo.json"):
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
        blue_alliance_data = extract_second_blue_team(matches)
        save_matches_to_file(blue_alliance_data)  # Saves to "BlueTwo.json"

if __name__ == "__main__":
    main()
