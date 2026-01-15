# mock-data/generate_voters.py
import json
import random
from datetime import datetime, timedelta
from faker import Faker
import os

# Initialize Faker with Indian locale
fake = Faker('en_IN')

# Sample data
INDIAN_STATES = ['Maharashtra', 'Karnataka', 'Delhi', 'Gujarat', 'Tamil Nadu', 'West Bengal']
CITIES = {
    'Maharashtra': ['Mumbai', 'Pune', 'Nagpur', 'Nashik'],
    'Karnataka': ['Bangalore', 'Mysore', 'Hubli', 'Mangalore'],
}

def generate_mock_voters(count=20):
    """Generate mock voter data"""
    voters = []
    
    for i in range(count):
        # Pick a random state first
        state_name = random.choice(list(CITIES.keys()))
        # Pick a city from that state
        city_name = random.choice(CITIES[state_name])
        
        # Generate date of birth (18-80 years old)
        dob = fake.date_of_birth(minimum_age=18, maximum_age=80)
        
        voter = {
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'date_of_birth': dob.isoformat(),
            'gender': random.choice(['MALE', 'FEMALE', 'OTHER']),
            'address_line1': fake.street_address(),
            # FIX: changed secondary_address() to street_name() because secondary_address doesn't exist in en_IN
            'address_line2': fake.street_name(), 
            'city': city_name,
            'state': state_name,
            'pincode': fake.postcode(), # fake.zipcode() is usually US, postcode works better globally
            'phone_number': f"+91{random.randint(7000000000, 9999999999)}",
            'email': f"{fake.user_name()}@example.com"
        }
        
        voters.append(voter)
    
    return voters

def generate_sample_photos():
    """Generate instructions for sample photos"""
    instructions = """
# Sample Photo Instructions

For a complete demo, you need sample face photos. Here are options:

## Option 1: Use Face Generation API (for demo)
1. Visit https://this-person-does-not-exist.com
2. Download 10-15 unique faces
3. Save them in mock-data/sample_photos/

## Option 2: Use Test Photos
1. Take selfies of team members
2. Ensure good lighting and clear face visibility
3. Save as JPG/PNG in mock-data/sample_photos/

## Option 3: Use Public Dataset
1. Download from https://github.com/NVlabs/ffhq-dataset (sample)
2. Select 10-15 diverse faces
3. Save in mock-data/sample_photos/

File naming: photo_001.jpg, photo_002.jpg, etc.
"""
    return instructions

if __name__ == "__main__":
    # Generate voter data
    voters = generate_mock_voters(20)
    
    # Save to JSON
    with open('voters.json', 'w') as f:
        json.dump(voters, indent=2, fp=f)
    
    print(f"✅ Generated {len(voters)} mock voters")
    print(f"📁 Saved to mock-data/voters.json")
    
    # Create photo directory
    os.makedirs('sample_photos', exist_ok=True)
    
    # Save photo instructions
    with open('sample_photos/README.txt', 'w') as f:
        f.write(generate_sample_photos())
    
    print("📸 Sample photo instructions saved to sample_photos/README.txt")