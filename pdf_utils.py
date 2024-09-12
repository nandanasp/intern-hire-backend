import requests

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

def download_file_from_google_drive(drive_url):
    download_url, id = get_google_drive_download_url(drive_url)
    response = requests.get(download_url)
    destination = 'resume/' + id + '.pdf'
    if response.status_code == 200:
        with open(destination, 'wb') as f:
            f.write(response.content)
        print(f"File successfully downloaded to {destination}")
        return destination
    else:
        print(f"Failed to download the file. Status code: {response.status_code}")
        return None  # Return None if the download failed



if __name__ == '__main__':
    url = "https://drive.google.com/file/d/1WQuS8nWNHHRPyGQs5cx7e2ttBEgbmLa7/view"
    resume_path = download_file_from_google_drive(url)
    print(resume_path)
