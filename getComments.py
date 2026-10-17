"""
YouTube Comment Collector - Get ALL possible comments
"""

import json
import time
import os
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# =============================================
# 🔑 CONFIGURATION
# =============================================

YOUR_API_KEY = "AIzaSyCGIRbw8n647lCdSUoHERJOOzsGflVxrZg"  # Your actual key
VIDEO_ID = "XS7itdfgNnU"
OUTPUT_DIR = "video_comments_all"

# =============================================
# 🚀 ENHANCED COLLECTOR
# =============================================

class YouTubeCommentCollector:
    def __init__(self):
        self.youtube = build('youtube', 'v3', developerKey=YOUR_API_KEY)
        self.video_id = VIDEO_ID
        self.output_dir = OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.all_comments = []
        self.comment_ids = set()  # Track unique comments
        self.stats = {
            'total': 0,
            'api_calls': 0,
            'start_time': None,
            'end_time': None
        }
        
        # Try different orderings to catch more comments
        self.order_options = ['time', 'relevance']  # 'time' gives newest, 'relevance' gives popular
        
    def fetch_with_retry(self, request_func, max_retries=3):
        """Fetch with retry logic."""
        for attempt in range(max_retries):
            try:
                response = request_func()
                self.stats['api_calls'] += 1
                return response
            except HttpError as e:
                if e.resp.status == 403 and 'quotaExceeded' in str(e):
                    print(f"⚠️  Quota exceeded! Waiting 60 seconds...")
                    time.sleep(60)
                elif attempt < max_retries - 1:
                    print(f"⚠️  Error, retrying in {2**attempt}s...")
                    time.sleep(2 ** attempt)
                else:
                    raise e
        return None
    
    def fetch_comments_page(self, page_token=None, order='time'):
        """Fetch one page of comments with specified order."""
        request = lambda: self.youtube.commentThreads().list(
            part='snippet',
            videoId=self.video_id,
            maxResults=100,
            pageToken=page_token,
            textFormat='plainText',
            order=order
        ).execute()
        
        return self.fetch_with_retry(request)
    
    def extract_comment(self, thread):
        """Extract comment data with all available fields."""
        snippet = thread['snippet']['topLevelComment']['snippet']
        return {
            'comment_id': thread['snippet']['topLevelComment']['id'],
            'author': snippet.get('authorDisplayName', 'Unknown'),
            'author_channel': snippet.get('authorChannelUrl', ''),
            'text': snippet.get('textDisplay', ''),
            'likes': snippet.get('likeCount', 0),
            'date': snippet.get('publishedAt', ''),
            'updated': snippet.get('updatedAt', ''),
            'reply_count': thread['snippet'].get('totalReplyCount', 0),
            'can_reply': thread['snippet'].get('canReply', True),
            'is_public': thread['snippet'].get('isPublic', True)
        }
    
    def collect_from_order(self, order, max_pages=None):
        """Collect comments using a specific ordering."""
        print(f"\n📊 Collecting with order: {order}")
        page_token = None
        page_num = 0
        new_comments = 0
        
        while True:
            page_num += 1
            if max_pages and page_num > max_pages:
                break
                
            response = self.fetch_comments_page(page_token, order)
            
            if not response or 'items' not in response:
                break
            
            # Process comments
            page_comments = 0
            for thread in response['items']:
                comment_id = thread['snippet']['topLevelComment']['id']
                
                # Only add if we haven't seen this comment before
                if comment_id not in self.comment_ids:
                    comment_data = self.extract_comment(thread)
                    self.all_comments.append(comment_data)
                    self.comment_ids.add(comment_id)
                    page_comments += 1
                    new_comments += 1
                    self.stats['total'] += 1
            
            print(f"  Page {page_num:3d} | Order: {order:9s} | +{page_comments:3d} new | Total: {self.stats['total']:6,d}")
            
            # Next page
            page_token = response.get('nextPageToken')
            if not page_token:
                break
            
            time.sleep(0.1)  # Small delay
        
        return new_comments
    
    def save_batch(self, comments, batch_num):
        """Save a batch of comments."""
        filename = f"comments_batch_{batch_num:03d}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'batch': batch_num,
                'count': len(comments),
                'collected_at': datetime.now().isoformat(),
                'video_id': self.video_id,
                'comments': comments
            }, f, ensure_ascii=False, indent=2)
        
        print(f"  💾 Saved batch {batch_num:03d} ({len(comments):,} comments)")
        return filepath
    
    def run(self):
        """Main collection method."""
        self.stats['start_time'] = datetime.now()
        print(f"\n🎬 YouTube Comment Collector (Enhanced)")
        print(f"📺 Video ID: {self.video_id}")
        print(f"📁 Output: {self.output_dir}/")
        print("=" * 60)
        
        batch_size = 5000
        batch_num = 1
        start_time = time.time()
        
        # Try different orderings to maximize comment collection
        for order in self.order_options:
            self.collect_from_order(order)
            
            # Save progress after each ordering
            if len(self.all_comments) >= batch_size:
                self.save_batch(self.all_comments[:batch_size], batch_num)
                self.all_comments = self.all_comments[batch_size:]
                batch_num += 1
            
            # Small pause between different orderings
            time.sleep(1)
        
        # Save remaining comments
        if self.all_comments:
            self.save_batch(self.all_comments, batch_num)
        
        # Final stats
        self.stats['end_time'] = datetime.now()
        self.print_summary()
    
    def print_summary(self):
        """Print final summary."""
        duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
        
        print("\n" + "="*60)
        print("✅ COLLECTION COMPLETE!")
        print("="*60)
        print(f"📺 Video ID: {self.video_id}")
        print(f"💬 Total unique comments: {self.stats['total']:,}")
        print(f"📞 API calls made: {self.stats['api_calls']}")
        print(f"📊 Quota used: {self.stats['api_calls']} / 10,000 ({self.stats['api_calls']/10000*100:.1f}%)")
        print(f"⏱️  Time taken: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        print(f"📁 Saved to: {os.path.abspath(self.output_dir)}/")
        print("="*60)
        
        # Compare with expected
        expected = 81200
        difference = expected - self.stats['total']
        if difference > 0:
            print(f"\n📊 Analysis:")
            print(f"   Expected: {expected:,} comments")
            print(f"   Got: {self.stats['total']:,} comments")
            print(f"   Missing: {difference:,} comments ({difference/expected*100:.1f}%)")
            print(f"\n💡 Missing comments could be:")
            print(f"   • Deleted comments")
            print(f"   • Comments marked as spam")
            print(f"   • Comments from blocked users")
            print(f"   • YouTube API limitations")

# =============================================
# 🎬 RUN IT
# =============================================

if __name__ == "__main__":
    collector = YouTubeCommentCollector()
    collector.run()