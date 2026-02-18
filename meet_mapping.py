# Updating the mapping based on user's corrected IDs
mapping_content = """# meet_mapping.py

# MyMeetScores (MMS) IDs for 2026 (Updated per user)
MMS_MEET_IDS = {
    "2026 Rose Gold Classic": "93352",
    "2026 Golden State Classic": "93657",
    "2026 Mardi Gras Invitational": "" # Add ID when available on MyMeetScores
}

# Local HTML Fallbacks for Ansel/MSO-Only (Dynamic scanning handles these in the main script)
"""

with open("meet_mapping.py", "w") as f:
    f.write(mapping_content)

print("Updated meet_mapping.py successfully.")
