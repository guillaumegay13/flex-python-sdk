from flex.flex_api_client import FlexApiClient
import csv
import os
import concurrent.futures
import time

base_url = os.environ['FLEX_ENV_URL'] # for exemple, https://my-env.com/api
username = os.environ['FLEX_ENV_USERNAME']
password = os.environ['FLEX_ENV_PASSWORD']

flex_api_client = FlexApiClient(base_url, username, password)

# Define exported CSV file name
filename = 'wrong_asset_keyframes.csv'

def write_next(filename, data):
    # Use a set to track unique entries
    unique_entries = set()
    
    # Check if the file exists
    if os.path.isfile(filename):
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                unique_entries.add(row[0])
    
    # Only append if not already present
    if data not in unique_entries:
        with open(filename, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([data])


def is_asset_keyframes_number_correct(asset_id):

    # Test on one asset first
    asset = flex_api_client.get_asset(asset_id)

    # Duration is in microseconds
    duration = asset.asset_context.video_stream_contexts[0].duration

    durationInSec = duration / 1000000

    # 2. Number of keyframes
    number_of_keyframes = flex_api_client.get_asset_keyframes_number(asset_id)

    # 3. Calculate theorical number of keyframes
    expected_number_of_keyframes = round(durationInSec / 5) + 1

    # 3. Compare
    if (expected_number_of_keyframes - number_of_keyframes < 2):
        # Maximum 1 keyframe difference is OK
        # print(f"Correct number of keyframes for asset {asset_id}")
        return True
    else:
        print(f"Number of keyframes is not correct for asset {asset_id}")
        return False

def process_asset(asset):
    try:
        if not is_asset_keyframes_number_correct(asset.id):
            return asset.id
    except Exception as e:
        print(f"Error checking asset {asset.id}: {e}")
    return None

def process_batch(batch, batch_number, total_batches):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(filter(None, executor.map(process_asset, batch)))
    print(f"Processed batch {batch_number}/{total_batches} - Found {len(results)} invalid assets")
    return results

def process_assets_parallel(assets, filename, batch_size=100):
    total_assets = len(assets)
    total_batches = (total_assets + batch_size - 1) // batch_size
    print(f"Starting to process {total_assets} assets in {total_batches} batches")
    
    start_time = time.time()
    invalid_count = 0

    with open(filename, 'a') as f:
        for i in range(0, total_assets, batch_size):
            batch = assets[i:i+batch_size]
            batch_number = i // batch_size + 1
            invalid_asset_ids = process_batch(batch, batch_number, total_batches)
            for asset_id in invalid_asset_ids:
                f.write(f"{asset_id}\n")
            invalid_count += len(invalid_asset_ids)

            # Print progress every 10 batches or on the last batch
            if batch_number % 10 == 0 or batch_number == total_batches:
                elapsed_time = time.time() - start_time
                progress = i / total_assets
                estimated_total_time = elapsed_time / progress if progress > 0 else 0
                remaining_time = estimated_total_time - elapsed_time
                print(f"Progress: {progress:.2%} - Elapsed: {elapsed_time:.2f}s - Estimated remaining: {remaining_time:.2f}s")

    total_time = time.time() - start_time
    print(f"Finished processing {total_assets} assets in {total_time:.2f} seconds")
    print(f"Found {invalid_count} invalid assets")

# Usage
print("Fetching assets...")
assets = flex_api_client.get_assets_parallel("assetType=File;fileType=Media;assetOrigin=Import;videoStreamCount=1")
print(f"Fetched {len(assets)} assets")

# Deduplicate Results
unique_assets = {asset.id: asset for asset in assets}.values()
assets = list(unique_assets)

print("Starting parallel processing of assets...")
process_assets_parallel(assets, filename)
print("Processing complete")