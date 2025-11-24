"""Setup rubric structure from case study Excel"""
import pandas as pd
from pathlib import Path

# Define rubric criteria based on case study requirements
rubric_data = [
    {
        'Criterion': 'Salutation',
        'Description': 'Quality of greeting at the beginning',
        'Keywords': 'hello,hi,good morning,good afternoon,good evening,good day,excited,introduce,feeling great',
        'Weight': 5,
        'Min_Words': 1,
        'Max_Words': 20
    },
    {
        'Criterion': 'Key Information',
        'Description': 'Presence of name, age, school, family, hobbies/interests',
        'Keywords': 'name,myself,age,years old,class,school,family,mother,father,sister,brother,hobbies,interest,like,enjoy,love,play,favorite',
        'Weight': 30,
        'Min_Words': 20,
        'Max_Words': 150
    },
    {
        'Criterion': 'Flow',
        'Description': 'Logical order: Salutation → Name → Details → Closing',
        'Keywords': 'first,then,also,finally,thank you,thanks',
        'Weight': 5,
        'Min_Words': 0,
        'Max_Words': 999
    },
    {
        'Criterion': 'Speech Rate',
        'Description': 'Appropriate speaking pace (words per minute)',
        'Keywords': '',
        'Weight': 10,
        'Min_Words': 0,
        'Max_Words': 999
    },
    {
        'Criterion': 'Grammar',
        'Description': 'Grammar correctness and proper sentence structure',
        'Keywords': '',
        'Weight': 10,
        'Min_Words': 0,
        'Max_Words': 999
    },
    {
        'Criterion': 'Vocabulary',
        'Description': 'Vocabulary richness and diversity (TTR)',
        'Keywords': '',
        'Weight': 10,
        'Min_Words': 0,
        'Max_Words': 999
    },
    {
        'Criterion': 'Clarity',
        'Description': 'Clear speech with minimal filler words',
        'Keywords': 'um,uh,like,you know,so,actually,basically,right,i mean,well,kinda,sort of,okay,hmm,ah',
        'Weight': 15,
        'Min_Words': 0,
        'Max_Words': 999
    },
    {
        'Criterion': 'Engagement',
        'Description': 'Positive sentiment, enthusiasm, and confidence',
        'Keywords': 'excited,happy,love,enjoy,great,wonderful,amazing,passionate,enthusiastic,interested',
        'Weight': 15,
        'Min_Words': 0,
        'Max_Words': 999
    }
]

# Create rubric DataFrame
df_rubric = pd.DataFrame(rubric_data)

# Read sample transcript from original Excel
original_file = Path("data/Case study for interns.xlsx")
df_original = pd.read_excel(original_file, sheet_name='Rubrics')
sample_transcript = df_original.iloc[6, 1]

# Create transcript DataFrame
transcript_data = [{
    'ID': 1,
    'Transcript': sample_transcript,
    'Word_Count': 131,
    'Expected_Score': 86,
    'Notes': 'Sample from Nirmaan AI case study'
}]
df_transcripts = pd.DataFrame(transcript_data)

# Write to Excel with Rubric and Transcripts sheets
with pd.ExcelWriter(original_file, mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
    df_rubric.to_excel(writer, sheet_name='Rubric', index=False)
    df_transcripts.to_excel(writer, sheet_name='Transcripts', index=False)

print("✓ Rubric and Transcripts sheets created successfully")
print(f"  - {len(df_rubric)} criteria (Total weight: {df_rubric['Weight'].sum()})")
print(f"  - {len(df_transcripts)} sample transcript(s)")
