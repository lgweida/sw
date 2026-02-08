#!/usr/bin/env python3
"""
Redis Binary File Consumer
Receive and reconstruct binary files from Redis Streams
"""

import redis
import os
import json
import base64
import hashlib
from collections import defaultdict
from datetime import datetime
from typing import Dict, List
import argparse

class RedisBinaryConsumer:
    def __init__(self, redis_url: str = None, consumer_group: str = "file-consumer", **redis_kwargs):
        """
        Initialize Redis connection and consumer group
        
        Args:
            redis_url: Redis connection URL
            consumer_group: Consumer group name
            **redis_kwargs: Additional Redis connection parameters
        """
        if redis_url:
            self.redis_client = redis.from_url(redis_url, **redis_kwargs)
        else:
            self.redis_client = redis.Redis(**redis_kwargs)
        
        self.consumer_group = consumer_group
        self.consumer_name = f"consumer-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Test connection
        try:
            self.redis_client.ping()
            print("✅ Connected to Redis successfully")
        except redis.ConnectionError:
            print("❌ Failed to connect to Redis")
            raise
        
        # Storage for file reconstruction
        self.files_in_progress = defaultdict(dict)
    
    def create_consumer_group(self, stream_name: str):
        """Create consumer group if it doesn't exist"""
        try:
            self.redis_client.xgroup_create(
                name=stream_name,
                groupname=self.consumer_group,
                id='0',
                mkstream=True
            )
            print(f"✅ Created consumer group: {self.consumer_group}")
        except redis.ResponseError as e:
            if "BUSYGROUP" in str(e):
                print(f"⚠️  Consumer group '{self.consumer_group}' already exists")
            else:
                raise
    
    def consume_files(self, stream_name: str, output_dir: str = "received_files", 
                      block_time: int = 5000, count: int = 10):
        """
        Consume binary files from Redis Stream
        
        Args:
            stream_name: Redis Stream name
            output_dir: Directory to save received files
            block_time: Block time in milliseconds (0 for non-blocking)
            count: Maximum number of messages to fetch at once
        """
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Create consumer group
        self.create_consumer_group(stream_name)
        
        print(f"👂 Listening on stream: {stream_name}")
        print(f"👥 Consumer group: {self.consumer_group}")
        print(f"👤 Consumer name: {self.consumer_name}")
        print(f"💾 Saving to: {os.path.abspath(output_dir)}")
        print("Press Ctrl+C to stop\n")
        
        last_id = '>'
        
        try:
            while True:
                try:
                    # Read messages from stream
                    messages = self.redis_client.xreadgroup(
                        groupname=self.consumer_group,
                        consumername=self.consumer_name,
                        streams={stream_name: last_id},
                        count=count,
                        block=block_time
                    )
                    
                    if not messages:
                        continue
                    
                    # Process messages
                    for stream, message_list in messages:
                        for message_id, message_data in message_list:
                            self._process_message(
                                stream_name=stream.decode('utf-8') if isinstance(stream, bytes) else stream,
                                message_id=message_id,
                                message_data=message_data,
                                output_dir=output_dir
                            )
                            
                            # Acknowledge message
                            self.redis_client.xack(
                                stream_name,
                                self.consumer_group,
                                message_id
                            )
                            
                            last_id = '>'
                
                except redis.ConnectionError as e:
                    print(f"⚠️  Connection error: {e}. Reconnecting...")
                    # Add reconnection logic here if needed
                    break
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping consumer...")
        finally:
            self.cleanup_pending_messages(stream_name)
            self.redis_client.close()
    
    def _process_message(self, stream_name: str, message_id: str, 
                         message_data: Dict, output_dir: str):
        """Process a single Redis Stream message"""
        # Convert byte keys to strings
        data = {}
        for key, value in message_data.items():
            key_str = key.decode('utf-8') if isinstance(key, bytes) else key
            if isinstance(value, bytes):
                try:
                    # Try to decode as UTF-8 first
                    value_str = value.decode('utf-8')
                    data[key_str] = value_str
                except UnicodeDecodeError:
                    # Keep as bytes if not decodable
                    data[key_str] = value
            else:
                data[key_str] = value
        
        msg_type = data.get('type', 'unknown')
        
        if msg_type == 'chunk':
            self._process_chunk(data, output_dir, message_id)
        elif msg_type == 'complete':
            self._process_completion(data, output_dir)
        else:
            print(f"⚠️  Unknown message type: {msg_type}")
    
    def _process_chunk(self, data: Dict, output_dir: str, message_id: str):
        """Process a file chunk"""
        try:
            chunk_data = json.loads(data.get('data', '{}'))
            file_name = chunk_data.get('file_name', 'unknown')
            chunk_index = chunk_data.get('chunk_index', 0)
            
            # Decode base64 data
            encoded_data = chunk_data.get('data', '')
            if encoded_data:
                binary_data = base64.b64decode(encoded_data)
                
                # Store chunk
                if file_name not in self.files_in_progress:
                    print(f"📥 Starting reception of: {file_name}")
                
                self.files_in_progress[file_name][chunk_index] = {
                    'data': binary_data,
                    'size': len(binary_data),
                    'received_at': datetime.now()
                }
                
                # Show progress
                total_chunks = len(self.files_in_progress[file_name])
                print(f"\r📥 {file_name}: {total_chunks} chunks received", end="")
        
        except (json.JSONDecodeError, KeyError, base64.binascii.Error) as e:
            print(f"⚠️  Error processing chunk {message_id}: {e}")
    
    def _process_completion(self, data: Dict, output_dir: str):
        """Process completion message and reconstruct file"""
        file_name = data.get('file_name', 'unknown')
        total_chunks = int(data.get('total_chunks', 0))
        file_size = int(data.get('file_size', 0))
        expected_hash = data.get('sha256', '')
        
        if file_name not in self.files_in_progress:
            print(f"\n⚠️  No chunks received for {file_name}")
            return
        
        chunks = self.files_in_progress[file_name]
        received_count = len(chunks)
        
        print(f"\n\n📦 Finalizing: {file_name}")
        print(f"   Expected chunks: {total_chunks}")
        print(f"   Received chunks: {received_count}")
        
        if received_count != total_chunks:
            print(f"⚠️  Warning: Missing {total_chunks - received_count} chunks")
            # Try to get missing chunks from pending messages
            self._recover_missing_chunks(file_name, total_chunks)
            chunks = self.files_in_progress[file_name]
            received_count = len(chunks)
        
        # Reconstruct file
        output_path = os.path.join(output_dir, file_name)
        sha256_hash = hashlib.sha256()
        total_reconstructed = 0
        
        try:
            with open(output_path, 'wb') as f:
                for i in range(total_chunks):
                    if i in chunks:
                        chunk_data = chunks[i]['data']
                        f.write(chunk_data)
                        sha256_hash.update(chunk_data)
                        total_reconstructed += len(chunk_data)
                    else:
                        print(f"   Missing chunk {i}")
            
            # Verification
            actual_hash = sha256_hash.hexdigest()
            actual_size = total_reconstructed
            
            print(f"📊 Reconstruction complete:")
            print(f"   File: {output_path}")
            print(f"   Size: {actual_size:,} bytes (expected: {file_size:,})")
            
            if expected_hash:
                if actual_hash == expected_hash:
                    print("✅ SHA256 verification: PASS")
                else:
                    print("❌ SHA256 verification: FAIL")
                    print(f"   Expected: {expected_hash}")
                    print(f"   Got:      {actual_hash}")
            else:
                print(f"   SHA256: {actual_hash}")
            
            # Verify file exists
            if os.path.exists(output_path):
                file_stats = os.stat(output_path)
                print(f"   Final file size: {file_stats.st_size:,} bytes")
            
            # Clean up
            del self.files_in_progress[file_name]
            
        except Exception as e:
            print(f"❌ Error reconstructing file: {e}")
        
        print("-" * 50)
    
    def _recover_missing_chunks(self, file_name: str, total_chunks: int):
        """Attempt to recover missing chunks from pending messages"""
        # This is a simplified version - you might want to implement
        # a more sophisticated recovery mechanism
        print(f"   Attempting to recover missing chunks for {file_name}...")
    
    def cleanup_pending_messages(self, stream_name: str):
        """Clean up pending messages when shutting down"""
        print("\n🧹 Cleaning up pending messages...")
        try:
            # Check for pending messages
            pending = self.redis_client.xpending(
                stream_name,
                self.consumer_group
            )
            print(f"   Pending messages: {pending}")
        except Exception as e:
            print(f"   Could not check pending messages: {e}")
    
    def list_consumer_groups(self, stream_name: str) -> List[Dict]:
        """List all consumer groups for a stream"""
        try:
            groups = self.redis_client.xinfo_groups(stream_name)
            return groups
        except Exception as e:
            print(f"Error listing consumer groups: {e}")
            return []

def main():
    parser = argparse.ArgumentParser(description='Consume binary files from Redis Streams')
    parser.add_argument('--redis-url', help='Redis URL (e.g., redis://localhost:6379)')
    parser.add_argument('--host', default='localhost', help='Redis host')
    parser.add_argument('--port', type=int, default=6379, help='Redis port')
    parser.add_argument('--password', help='Redis password')
    parser.add_argument('--stream', default='binary-files', help='Redis Stream name')
    parser.add_argument('--group', default='file-consumer', help='Consumer group name')
    parser.add_argument('--output-dir', default='received_files', help='Output directory')
    parser.add_argument('--block-time', type=int, default=5000, help='Block time in ms (0 for non-blocking)')
    
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
        # Initialize consumer
        consumer = RedisBinaryConsumer(
            consumer_group=args.group,
            **redis_params
        )
        
        # Start consuming
        consumer.consume_files(
            stream_name=args.stream,
            output_dir=args.output_dir,
            block_time=args.block_time
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Consumer stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()