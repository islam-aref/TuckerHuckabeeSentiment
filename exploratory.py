"""
Word Count Distribution - Line Chart
Similar to the example image: Number of Words vs Number of Reviews/Comments
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# =============================================
# 🔧 CONFIGURATION
# =============================================

INPUT_EXCEL = "youtube_comments_master.xlsx"
OUTPUT_GRAPH = "comment_word_count_linechart.png"

# =============================================
# 📊 CREATE WORD COUNT DISTRIBUTION
# =============================================

print("\n📂 Loading comments...")
print("=" * 60)

# Load comments
df = pd.read_excel(INPUT_EXCEL, sheet_name='Comments')
print(f"✅ Loaded {len(df):,} comments")

# Calculate word count for each comment
print("\n📝 Calculating word counts...")
df['word_count'] = df['text'].astype(str).apply(lambda x: len(str(x).split()))

# =============================================
# 📈 CREATE LINE CHART (like the example)
# =============================================

print("\n📈 Creating line chart...")

# Group by word count and count number of comments
word_count_distribution = df['word_count'].value_counts().sort_index()

# Filter to a reasonable range (like the example: 0-50 words)
# The example shows up to 50 words, so we'll focus on that range
max_words_to_show = 50
distribution_filtered = word_count_distribution[word_count_distribution.index <= max_words_to_show]

# Create the line chart
plt.figure(figsize=(12, 6))
plt.style.use('default')  # Use default style for cleaner look

# Plot the line
plt.plot(distribution_filtered.index, distribution_filtered.values, 
         marker='o', markersize=4, linewidth=2, color='#1f77b4')

# Customize the chart to match the example
plt.xlabel('Number of Words in Comment', fontsize=12)
plt.ylabel('Number of Comments', fontsize=12)
plt.title('Distribution of Comment Lengths', fontsize=14, fontweight='bold')

# Set x-axis to show every 5 words
plt.xticks(np.arange(0, max_words_to_show + 1, 5))
plt.xlim(0, max_words_to_show)

# Add grid for better readability
plt.grid(True, alpha=0.3, linestyle='--')

# Add value labels on key points (every 10 words)
for i in range(0, max_words_to_show + 1, 10):
    if i in distribution_filtered.index:
        plt.text(i, distribution_filtered[i] + 200, 
                f'{distribution_filtered[i]:,}', 
                ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig(OUTPUT_GRAPH, dpi=300, bbox_inches='tight')
print(f"✅ Line chart saved to: {os.path.abspath(OUTPUT_GRAPH)}")

# =============================================
# 📊 CREATE A MORE DETAILED VERSION (like the table in your image)
# =============================================

print("\n📊 Creating detailed distribution table...")

# Create a table similar to what you shared
# The example had: 
# Number of Words in Review | Number of Reviews
# 0 | 5000
# 1 | 023000 (23,000)
# 2 | 010000 (10,000)
# etc.

# Get distribution for words 0-50
distribution_table = []
for word_count in range(0, 51):
    count = word_count_distribution.get(word_count, 0)
    distribution_table.append({
        'Number of Words': word_count,
        'Number of Comments': count,
        'Percentage': (count / len(df)) * 100
    })

dist_df = pd.DataFrame(distribution_table)

# Format the numbers to match the style in your image
dist_df['Number of Comments (formatted)'] = dist_df['Number of Comments'].apply(
    lambda x: f"{x:06,d}" if x < 1000000 else f"{x/1000000:.1f}M"
)

print("\n📋 Distribution Table (first 20 rows):")
print("=" * 50)
print(dist_df[['Number of Words', 'Number of Comments (formatted)']].head(20).to_string(index=False))

# =============================================
# 📈 CREATE A CLEANER LINE CHART (exactly like the example)
# =============================================

plt.figure(figsize=(14, 7))

# Create two subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

# First plot - Line chart like the example
ax1.plot(distribution_filtered.index, distribution_filtered.values, 
         marker='o', markersize=3, linewidth=1.5, color='black')
ax1.set_xlabel('Number of Words in Comment', fontsize=11)
ax1.set_ylabel('Number of Comments', fontsize=11)
ax1.set_title('Comment Length Distribution', fontsize=13, fontweight='bold')
ax1.set_xticks(np.arange(0, max_words_to_show + 1, 5))
ax1.set_xlim(0, max_words_to_show)
ax1.grid(True, alpha=0.3, linestyle=':')
ax1.axvline(x=df['word_count'].median(), color='red', linestyle='--', 
            alpha=0.7, label=f'Median: {df["word_count"].median():.0f}')
ax1.legend()

# Second plot - Bar chart version for comparison
ax2.bar(distribution_filtered.index[:30], distribution_filtered.values[:30], 
        width=0.8, color='skyblue', edgecolor='navy', alpha=0.7)
ax2.set_xlabel('Number of Words', fontsize=11)
ax2.set_ylabel('Number of Comments', fontsize=11)
ax2.set_title('Comment Length (First 30 Words)', fontsize=13, fontweight='bold')
ax2.set_xticks(np.arange(0, 31, 5))
ax2.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('comment_word_count_detailed.png', dpi=300, bbox_inches='tight')
print("✅ Detailed chart saved to: comment_word_count_detailed.png")

# =============================================
# 💾 SAVE THE DISTRIBUTION TABLE TO EXCEL
# =============================================

output_excel = "comment_word_count_distribution.xlsx"
with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
    # Full distribution
    dist_df.to_excel(writer, sheet_name='Word_Count_Distribution', index=False)
    
    # Summary statistics
    stats_data = {
        'Statistic': ['Total Comments', 'Mean', 'Median', 'Mode', 'Min', 'Max',
                     'Most Common Length', 'Comments with 0-5 words', 
                     'Comments with 6-10 words', 'Comments with 11-20 words'],
        'Value': [
            f"{len(df):,}",
            f"{df['word_count'].mean():.1f}",
            f"{df['word_count'].median():.0f}",
            f"{df['word_count'].mode()[0]}",
            f"{df['word_count'].min()}",
            f"{df['word_count'].max()}",
            f"{df['word_count'].mode()[0]} words ({word_count_distribution.get(df['word_count'].mode()[0], 0):,} comments)",
            f"{df[df['word_count'] <= 5].shape[0]:,}",
            f"{df[(df['word_count'] > 5) & (df['word_count'] <= 10)].shape[0]:,}",
            f"{df[(df['word_count'] > 10) & (df['word_count'] <= 20)].shape[0]:,}"
        ]
    }
    stats_df = pd.DataFrame(stats_data)
    stats_df.to_excel(writer, sheet_name='Summary', index=False)
    
    # Raw data for chart recreation
    chart_data = pd.DataFrame({
        'word_count': distribution_filtered.index,
        'number_of_comments': distribution_filtered.values
    })
    chart_data.to_excel(writer, sheet_name='Chart_Data', index=False)

print(f"\n✅ Distribution table saved to: {os.path.abspath(output_excel)}")

# =============================================
# 📊 PRINT KEY INSIGHTS
# =============================================

print("\n" + "=" * 60)
print("📊 Key Insights from Word Count Distribution")
print("=" * 60)

# Peak distribution
peak_word_count = distribution_filtered.idxmax()
peak_count = distribution_filtered.max()
print(f"\n📈 Peak: Most comments have {peak_word_count} words ({peak_count:,} comments)")

# Short comments (1-5 words)
short_comments_pct = (df[df['word_count'] <= 5].shape[0] / len(df)) * 100
print(f"📝 Short comments (1-5 words): {short_comments_pct:.1f}% of all comments")

# Medium comments (6-20 words)
medium_comments_pct = (df[(df['word_count'] > 5) & (df['word_count'] <= 20)].shape[0] / len(df)) * 100
print(f"📄 Medium comments (6-20 words): {medium_comments_pct:.1f}% of all comments")

# Long comments (21+ words)
long_comments_pct = (df[df['word_count'] > 20].shape[0] / len(df)) * 100
print(f"📚 Long comments (21+ words): {long_comments_pct:.1f}% of all comments")

# Find the top 5 word counts
print("\n🏆 Top 5 most common comment lengths:")
top_5 = distribution_filtered.nlargest(5)
for word_count, count in top_5.items():
    print(f"   • {word_count} words: {count:,} comments ({count/len(df)*100:.1f}%)")

print(f"\n✅ Line chart saved as: {OUTPUT_GRAPH}")