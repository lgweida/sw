#!/usr/bin/env python3
"""
Redis Binary File Publisher
Send binary files to Redis Streams (compatible with Render Redis)
"""

import redis
import os
import hashlib
import json
import base64
from typing import Dict, List
import argparse
from pathlib import Path

class RedisBinaryPublisher:
    def __init__(self, redis_url: str = None, **redis_kwargs):
        """
        Initialize Redis connection
        
        Args:
            redis_url: Redis connection URL (for Render: redis://red-xxx:6379)
            **redis_kwargs: Additional Redis connection parameters
        """
        if redis_url:
            self.redis_client = redis.from_url(redis_url, **redis_kwargs)
        else:
            self.redis_client = redis.Redis(**redis_kwargs)
        
        # Test connection
        try:
            self.redis_client.ping()
            print("✅ Connected to Redis successfully")
        except redis.ConnectionError:
            print("❌ Failed to connect to Redis")
            raise
    
    def publish_file(self, stream_name: str, file_path: str, chunk_size: int = 500000) -> Dict:
        """
        Publish a binary file to Redis Stream in chunks
        
        Args:
            stream_name: Redis Stream name
            file_path: Path to binary file
            chunk_size: Size of each chunk (default: 500KB)
        
        Returns:
            Dictionary with transfer information
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        file_hash = hashlib.sha256()
        
        print(f"📤 Publishing: {file_name}")
        print(f"📊 File size: {file_size:,} bytes")
        print(f"📦 Chunk size: {chunk_size:,} bytes")
        
        # Read and publish file in chunks
        chunk_count = 0
        chunk_ids = []
        
        try:
            with open(file_path, 'rb') as file:
                while True:
                    chunk = file.read(chunk_size)
                    if not chunk:
                        break
                    
                    # Update hash
                    file_hash.update(chunk)
                    
                    # Prepare message
                    message = {
                        'file_name': file_name,
                        'chunk_index': chunk_count,
                        'total_chunks': -1,  # Will be updated later
                        'file_size': file_size,
                        'chunk_size': len(chunk),
                        'data': base64.b64encode(chunk).decode('utf-8'),
                        'is_last': False
                    }
                    
                    # Add to Redis Stream
                    msg_id = self.redis_client.xadd(
                        name=stream_name,
                        fields={
                            'type': 'chunk',
                            'data': json.dumps(message)
                        },
                        maxlen=1000  # Keep last 1000 messages
                    )
                    
                    chunk_ids.append(str(msg_id, 'utf-8') if isinstance(msg_id, bytes) else msg_id)
                    chunk_count += 1
                    
                    # Show progress
                    progress = (file.tell() / file_size) * 100
                    print(f"\r📤 Progress: {progress:.1f}% ({chunk_count} chunks)", end="")
            
            print()  # New line after progress
            
            # Send completion message
            completion_msg = {
                'type': 'complete',
                'file_name': file_name,
                'total_chunks': chunk_count,
                'file_size': file_size,
                'sha256': file_hash.hexdigest(),
                'chunk_size': chunk_size,
                'chunk_ids': json.dumps(chunk_ids)
            }
            
            completion_id = self.redis_client.xadd(
                name=stream_name,
                fields=completion_msg,
                maxlen=1000
            )
            
            print(f"✅ File published successfully!")
            print(f"   Stream: {stream_name}")
            print(f"   Chunks: {chunk_count}")
            print(f"   SHA256: {file_hash.hexdigest()}")
            print(f"   Completion ID: {completion_id}")
            
            return {
                'file_name': file_name,
                'file_size': file_size,
                'chunks': chunk_count,
                'sha256': file_hash.hexdigest(),
                'stream': stream_name,
                'completion_id': str(completion_id, 'utf-8') if isinstance(completion_id, bytes) else completion_id
            }
            
        except Exception as e:
            print(f"❌ Error publishing file: {e}")
            raise
    
    def list_streams(self, pattern: str = "*") -> List[str]:
        """List all streams matching pattern"""
        return [key.decode('utf-8') if isinstance(key, bytes) else key 
                for key in self.redis_client.keys(pattern)]
    
    def get_stream_info(self, stream_name: str) -> Dict:
        """Get information about a stream"""
        try:
            info = self.redis_client.xinfo_stream(stream_name)
            return {k.decode('utf-8') if isinstance(k, bytes) else k: 
                    v.decode('utf-8') if isinstance(v, bytes) else v 
                    for k, v in info.items()}
        except Exception as e:
            return {'error': str(e)}
    
    def close(self):
        """Close Redis connection"""
        self.redis_client.close()

def main():
    parser = argparse.ArgumentParser(description='Publish binary files to Redis Streams')
    parser.add_argument('--redis-url', help='Redis URL (e.g., redis://localhost:6379)')
    parser.add_argument('--host', default='localhost', help='Redis host')
    parser.add_argument('--port', type=int, default=6379, help='Redis port')
    parser.add_argument('--password', help='Redis password')
    parser.add_argument('--stream', default='binary-files', help='Redis Stream name')
    parser.add_argument('--chunk-size', type=int, default=500000, help='Chunk size in bytes')
    parser.add_argument('file', help='File to publish')
    
    args = parser.parse_args()
    
    # Prepare connection parameters
    redis_params = {}
    
    if args.redis_url:
        redis_params['redis_url'] = args.redis_url
    else:
        redis_params['host'] = args.host
        redis_params['port'] = args.port
        if args.password:
            redis_params['password'] = args.password
    
    try:
        # Initialize publisher
        publisher = RedisBinaryPublisher(**redis_params)
        
        # Optional: Show stream info before publishing
        print(f"📡 Stream info for '{args.stream}':")
        stream_info = publisher.get_stream_info(args.stream)
        if 'error' not in stream_info:
            print(f"   Length: {stream_info.get('length', 'N/A')} messages")
            print(f"   Groups: {stream_info.get('groups', 'N/A')}")
        else:
            print(f"   Stream doesn't exist or error: {stream_info['error']}")
        
        print("-" * 50)
        
        # Publish file
        result = publisher.publish_file(args.stream, args.file, args.chunk_size)
        
        # Print summary
        print("\n📋 Publish Summary:")
        for key, value in result.items():
            print(f"   {key}: {value}")
        
        # Close connection
        publisher.close()
        
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()