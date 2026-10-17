import pandas as pd
import re
from collections import Counter
import nltk
from nltk.corpus import stopwords

# 1. Download the stop words list (only needs to be done once)
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

# 2. Load the Excel file
# Replace 'your_file_name.xlsx' with your actual file path
df = pd.read_excel('youtube_comments_master.xlsx')

# 3. Join text and clean
# Convert text to lowercase and split into words
text_data = " ".join(df['text'].astype(str)).lower()
words = re.findall(r'\b\w+\b', text_data)

# 4. Filter out stop words and single characters (like 'i' or 'a')
filtered_words = [word for word in words if word not in stop_words and len(word) > 1]

# 5. Count frequencies
word_counts = Counter(filtered_words)

# 6. Convert to DataFrame and Export
freq_df = pd.DataFrame(word_counts.items(), columns=['word', 'frequency'])
freq_df = freq_df.sort_values(by='frequency', ascending=False)

# Save to CSV
freq_df.to_csv('word_frequency_refined.csv', index=False)

print("Refined CSV 'word_frequency_refined.csv' has been created successfully!")