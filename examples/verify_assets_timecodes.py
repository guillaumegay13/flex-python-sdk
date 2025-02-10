from flex import FlexApiClient
import csv
from timecode import Timecode
import os
base_url = os.getenv("FLEX_BASE_URL")
username = os.getenv("FLEX_USERNAME")
password = os.getenv("FLEX_PASSWORD")

flex_api_client: FlexApiClient = FlexApiClient(base_url, username, password)

# Get all video assets
assets = flex_api_client.get_assets_parallel(filters="variant=MDA;assetOrigin=Import")

# Extract asset IDs
asset_ids = [asset.id for asset in assets]

# Write to CSV file
with open('exported_asset_ids.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Asset ID'])
    for asset_id in asset_ids:
        writer.writerow([asset_id])

print(f"Successfully exported {len(asset_ids)} asset IDs to exported_asset_ids.csv")

# Check if the timecodes in the metadata and from the asset are consistent
def verify_timecode_consistency(bcd_timecode_us: int, tc_in: str, tc_out: str, duration_us: int, frame_rate: float = 29.97, preferred_drop_frame: bool = True, drop_frame_from_string: bool = True) -> bool:
    """
    Verify that microseconds timecode matches the formatted timecode string and check duration consistency
    
    Args:
        bcd_timecode_us: Timecode in microseconds (e.g., 62112750700) from the asset format context
        tc_in: Formatted timecode string (e.g., "17:15:13:02") from metadata
        tc_out: Formatted timecode string (e.g., "18:10:02:17") from metadata
        duration_us: Duration in microseconds from the asset format context
        frame_rate: from the asset video stream context
        preferred_drop_frame: from the asset format context
        drop_frame_from_string: from the asset metadata
    
    Returns:
        bool: True if timecodes are consistent, False otherwise
    """
    # Convert microseconds to frames for start time
    seconds = bcd_timecode_us / 1_000_000
    frames_from_us = int(seconds * frame_rate)
    
    # Convert duration microseconds to frames
    duration_seconds = duration_us / 1_000_000
    duration_frames = int(duration_seconds * frame_rate)
    
    # Create Timecode objects
    tc_from_us = Timecode(frame_rate, frames=frames_from_us)
    tc_from_string = Timecode(frame_rate, tc_in)
    tc_out_obj = Timecode(frame_rate, tc_out)
    
    # Set drop frame for all timecode objects
    tc_from_us.drop_frame = preferred_drop_frame
    tc_from_string.drop_frame = drop_frame_from_string
    tc_out_obj.drop_frame = preferred_drop_frame
    
    # Calculate expected duration in frames
    calculated_duration = tc_out_obj.frames - tc_from_string.frames
    
    # Verify all conditions
    timecode_match = abs(tc_from_us.frames == tc_from_string.frames) <= 1 # Allow 1 frame tolerance due to rounding
    duration_match = abs(calculated_duration - duration_frames) <= 1  # Allow 1 frame tolerance due to rounding
    
    if not timecode_match:
        print(f"Start Timecode mismatch:")
        print(f"  From μs: {tc_from_us} ({tc_from_us.frames} frames)")
        print(f"  From string: {tc_from_string} ({tc_from_string.frames} frames)")
        print(f"  Difference: {abs(tc_from_us.frames - tc_from_string.frames)} frames")
    
    if not duration_match:
        print(f"Duration mismatch:")
        print(f"  Expected (from μs): {duration_frames} frames ({duration_us} μs)")
        print(f"  Calculated: {calculated_duration} frames")
        print(f"  Difference: {abs(duration_frames - calculated_duration)} frames")
    
    return timecode_match and duration_match

def extract_drop_frame_from_frame_rate(frame_rate_str: str) -> bool:
    """
    Extract drop frame information from frame rate string
    
    Args:
        frame_rate_str: Frame rate string (e.g., "29.97(DF)" or "29.97")
    
    Returns:
        bool: True if drop frame, False otherwise
    """
    return "(DF)" in frame_rate_str

def verify_asset_metadata(asset_id):
    asset = flex_api_client.get_asset(asset_id=asset_id, include_metadata=True)
    
    verify_timecode_consistency(
        bcd_timecode_us=asset.asset_context.format_context.preferred_start_timecode,
        tc_in=asset.metadata['tc-in']['time'],
        tc_out=asset.metadata['tc-out']['time'],
        duration_us=asset.asset_context.format_context.duration,
        frame_rate=asset.asset_context.video_stream_contexts[0].frame_rate,
        preferred_drop_frame=asset.asset_context.format_context.preferred_drop_frame,
        drop_frame_from_string=extract_drop_frame_from_frame_rate(asset.metadata['tc-in']['frame-rate'])
    )

assets_with_inconsistent_timecodes = []
for asset_id in asset_ids:
    if not verify_asset_metadata(asset_id):
        assets_with_inconsistent_timecodes.append(asset_id)

print(f"Assets with inconsistent timecodes: {assets_with_inconsistent_timecodes}")
