import requests, re

def get_google_drive_download_url(drive_url):
    # Check if the URL is of the format "open?id="
    if "open?id=" in drive_url:
        file_id = drive_url.split("open?id=")[1]
    # Check if the URL is of the format "file/d/"
    elif "file/d/" in drive_url:
        file_id = drive_url.split('/d/')[1].split('/')[0]
    else:
        raise ValueError("The provided URL is not a valid Google Drive URL")
    
    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    return download_url, file_id

def get_google_drive_download_url(drive_url):
    try:
        # Handling both types of Google Drive links
        file_id = None
        match = re.search(r'(?:/d/|id=)([a-zA-Z0-9-_]+)', drive_url)
        if match:
            file_id = match.group(1)
        if not file_id:
            raise ValueError(f"Invalid Google Drive URL: {drive_url}")
        
        download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        return download_url, file_id
    except Exception as e:
        print(f"Error extracting download URL from {drive_url}: {e}")
        raise

def download_file_from_google_drive(drive_url):
    try:
        # Get download URL and file ID
        download_url, file_id = get_google_drive_download_url(drive_url)

        # Make the request to download the file
        response = requests.get(download_url)
        destination = f'resume/{file_id}.pdf'

        # Check the response status code
        if response.status_code == 200:
            with open(destination, 'wb') as f:
                f.write(response.content)
            return destination
        else:
            print(f"Failed to download the file from {drive_url}. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error downloading the file from {drive_url}: {e}")
        return None

if __name__ == '__main__':
    arr = ["https://drive.google.com/open?id=1zBqEdYjypU6zPpBrh5mO-bp2YSlQQmLW"]
    for url in arr:
        resume_path = download_file_from_google_drive(url)
        print(resume_path)

