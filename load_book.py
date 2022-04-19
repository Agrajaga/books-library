import os
import requests




if __name__ == "__main__":


    for index in range(1, 11):
        params = {
            "id": index,
        }
        response = requests.get("https://tululu.org/txt.php", params=params)
        response.raise_for_status()
        
        os.makedirs("books", exist_ok=True)
        with open(f"books/id{index}.txt", "w") as f:
            f.write(response.text)
