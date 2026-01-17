#!/usr/bin/env python3
"""Quick script to check processing results"""
import json
from pathlib import Path

outputs_dir = Path("outputs")

print("🔍 Checking PulsePoint AI Processing Results\n")
print("=" * 60)

# Find all metadata files
metadata_files = list(outputs_dir.glob("*_metadata.json"))

if not metadata_files:
    print("❌ No processing results found")
    print("\nTip: Upload a video through the web interface first!")
    exit(1)

print(f"Found {len(metadata_files)} processed video(s)\n")

for meta_file in sorted(metadata_files, key=lambda x: x.stat().st_mtime, reverse=True):
    print(f"\n📁 {meta_file.name}")
    print("-" * 60)
    
    with open(meta_file) as f:
        data = json.load(f)
    
    job_id = data['job_id']
    clips = data.get('clips', [])
    
    print(f"Job ID: {job_id}")
    print(f"Clips generated: {len(clips)}")
    
    if clips:
        print("\n✅ SUCCESS! Clips created:")
        for clip in clips:
            print(f"  - {clip['filename']}")
            print(f"    Duration: {clip['duration']:.1f}s")
            print(f"    Headline: {clip['headline']}")
    else:
        print("\n⚠️  NO CLIPS CREATED")
        print("Reason: Transcription or AI analysis failed")
        
        # Check what worked
        peaks = len(data.get('emotional_peaks', []))
        ai_moments = len(data.get('ai_moments', []))
        segments = data.get('transcription_summary', {}).get('total_segments', 0)
        
        print(f"\nDiagnostics:")
        print(f"  Audio peaks detected: {peaks} ✓" if peaks > 0 else f"  Audio peaks: {peaks} ✗")
        print(f"  Transcription segments: {segments} ✓" if segments > 0 else f"  Transcription segments: {segments} ✗ (AssemblyAI failed)")
        print(f"  AI moments found: {ai_moments} ✓" if ai_moments > 0 else f"  AI moments: {ai_moments} ✗ (Gemini failed)")

print("\n" + "=" * 60)
print("\n💡 To fix issues:")
print("   1. Check that API keys are valid")
print("   2. Restart the server: python run.py")
print("   3. Re-upload your video")
