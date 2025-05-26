import sqlite3
import os

# Ensure images directory exists
os.makedirs("images", exist_ok=True)

# Initialize the database and create the prompts table if it doesn't exist
def init_db(db_name='prompts.db'):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS prompts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prompt TEXT NOT NULL,
        expected_style TEXT NOT NULL,
        image TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

# Connect to the SQLite database
def connect_db(db_name='prompts.db'):
    return sqlite3.connect(db_name)

# Insert a new prompt into the database
def insert_prompt(conn, prompt, expected_style, image):
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO prompts (prompt, expected_style, image)
    VALUES (?, ?, ?)
    ''', (prompt, expected_style, image))
    conn.commit()

# Fetch all prompts from the database
def fetch_prompts(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT prompt, expected_style, image FROM prompts')
    return cursor.fetchall()

# Fetch only images from the database
def fetch_images(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT prompt, image FROM prompts')
    return cursor.fetchall()

# Main execution
if __name__ == "__main__":
    # Initialize the database
    init_db()

    # Connect to the database
    connection = connect_db()

    # Example usage: Insert mock data
    mock_data = [
        ("a fantasy castle in the clouds", "realistic", "images/castle.png"),
        ("a futuristic robot chef in a kitchen", "cyberpunk", "images/robot.png"),
        ("a panda riding a bicycle in space", "cartoon", "images/panda.png"),
        ("a serene landscape with mountains and a river", "oil painting", "url/to/landscape/image.png"),
        ("a retro video game character jumping over obstacles", "pixel art", "url/to/pixelart/image.png"),
        ("a magical forest with glowing creatures", "animation", "url/to/forest/image.png"),
        ("an intricate geometric pattern in vibrant colors", "Geometric & Fractal Art", "url/to/geometric/image.png"),
        ("a futuristic city skyline at sunset", "Architectural", "url/to/city/image.png"),
        ("a cozy cottage in the woods", "Traditional", "url/to/cottage/image.png"),
        ("a swirling mix of colors and shapes", "Abstract", "url/to/abstract/image.png"),
        ("a sleek modern office building", "Modern & Digital", "url/to/modern/image.png"),
        ("an alien planet with strange landscapes", "Fantasy & Sci-Fi", "url/to/alien/image.png"),
        ("a group of superheroes in action", "Cartoon & Comics", "url/to/superheroes/image.png")
    ]

    # Insert mock data into the database
    for prompt_data in mock_data:
        insert_prompt(connection, *prompt_data)

    # Fetch and print all prompts
    prompts = fetch_prompts(connection)
    print("Prompts:")
    for prompt in prompts:
        print(prompt)

    # Fetch and print all images
    images = fetch_images(connection)
    print("\nImages:")
    for image in images:
        print(image)

    # Close the database connection
    connection.close()