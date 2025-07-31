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

# Function to extract only the THIRD blue alliance team
def extract_third_blue_team(matches):
    blue_matches = {}
    
    # Filter only qualification matches
    qual_matches = [m for m in matches if m.get('comp_level') == 'qm']
    
    if not qual_matches:
        print("No qualification matches found.")
        return {"Blue 3": blue_matches}
    
    # Sort qualification matches by match number
    sorted_matches = sorted(qual_matches, key=lambda m: m.get('match_number', 0))
    
    # Ensure first qualification match is handled separately
    first_match = sorted_matches[0]
    first_match_number = first_match.get('match_number')
    first_blue_teams = first_match.get('alliances', {}).get('blue', {}).get('team_keys', [])
    
    if len(first_blue_teams) >= 3:
        first_third_blue_team = first_blue_teams[2][3:] if first_blue_teams[2].startswith("frc") else first_blue_teams[2]
        blue_matches[str(first_match_number)] = {
            "match_number": str(first_match_number),
            "team": {"number": first_third_blue_team, "color": "blue"}
        }
    
    # Process the rest of the qualification matches normally
    for match in sorted_matches[1:]:
        match_number = match.get('match_number')
        if match_number is None:
            continue

        blue_teams = match.get('alliances', {}).get('blue', {}).get('team_keys', [])
        
        if len(blue_teams) >= 3:
            third_blue_team = blue_teams[2][3:] if blue_teams[2].startswith("frc") else blue_teams[2]
            blue_matches[str(match_number)] = {
                "match_number": str(match_number),
                "team": {"number": third_blue_team, "color": "blue"}
            }
    
    return {"Blue 3": blue_matches}  # Wrap in "Blue 3" key

# Function to save blue alliance data to a JSON file
def save_matches_to_file(matches_data, filename="BlueThree.json"):
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
        blue_alliance_data = extract_third_blue_team(matches)
        save_matches_to_file(blue_alliance_data)  # Saves to "BlueThree.json"

if __name__ == "__main__":
    main()
