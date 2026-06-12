import pandas as pd
import os
from pymongo import MongoClient

# MongoDB Connection
MONGODB_URI="mongodb+srv://yousefmegawer_db_user:Yousef123@cluster0.ub07l8c.mongodb.net/?appName=Cluster0"
client = MongoClient(MONGODB_URI)
db = client["kayfa_analytics"]

# Path to your cleaned data
base_path = './cleaned_data'

# Upload main datasets
files = {
    'students': 'students_clean.csv',
    'groups': 'groups_clean.csv',
    'courses': 'courses_clean.csv',
    'grades': 'grades_clean.csv',
    'attendance': 'attendance_clean.csv',
    'concepts': 'concepts_clean.csv',
    'engagement': 'engagement_clean.csv',
    'submissions': 'submissions_clean.csv',
    'full_model': 'full_model.csv',
}

# Question aggregates
questions = {
    'q1_attendance': 'q1_attendance_by_group.csv',
    'q2_scores': 'q2_score_distribution.csv',
    'q3_courses': 'q3_course_performance.csv',
    'q4_correlation': 'q4_attendance_grade_correlation.csv',
    'q4_scatter': 'q4_scatter_data.csv',
    'q5_engagement': 'q5_engagement_correlation.csv',
    'q5_scatter': 'q5_scatter_data.csv',
    'q6_concepts': 'q6_concept_failures.csv',
    'q7_trends': 'q7_weakest_concept_trend.csv',
    'q8_late': 'q8_late_submission_impact.csv',
    'q9_cohort': 'q9_cohort_trends.csv',
    'q10_age': 'q10_age_analysis.csv',
    'q11_segments': 'q11_student_segments.csv',
    'q12_groups': 'q12_group_size_comparison.csv',
    'q13_viability': 'q13_group_viability.csv',
    'q13_metrics': 'q13_group_metrics.csv',
    'q14_risk': 'q14_at_risk_students.csv',
    'q15_trends': 'q15_group_trends_monthly.csv',
}

def upload_collection(collection_name, csv_filename):
    """Upload CSV to MongoDB collection"""
    filepath = os.path.join(base_path, csv_filename)
    
    if not os.path.exists(filepath):
        print(f"Missing: {filepath}")
        return False
    
    try:
        # Read CSV
        df = pd.read_csv(filepath)
        
        if df.empty:
            print(f"Empty CSV: {csv_filename}")
            return False
        
        # Convert to records
        records = df.to_dict('records')
        
        # Clear existing collection
        db[collection_name].delete_many({})
        
        # Insert records - FIX: Use .inserted_ids instead of result
        result = db[collection_name].insert_many(records)
        
        num_inserted = len(result.inserted_ids)  # CORRECT WAY
        
        print(f"{collection_name:20} → {num_inserted:4} documents")
        return True
    
    except Exception as e:
        print(f"{collection_name:20} → {str(e)[:60]}")
        return False

print("=" * 70)
print("Uploading main datasets...")
print("=" * 70)

success_count = 0
for name, filename in files.items():
    if upload_collection(name, filename):
        success_count += 1

print("\n" + "=" * 70)
print("Uploading question aggregates...")
print("=" * 70)

for name, filename in questions.items():
    if upload_collection(name, filename):
        success_count += 1

print("\n" + "=" * 70)
print(f"Upload Complete! {success_count}/{len(files) + len(questions)} collections uploaded")
print("=" * 70)

client.close()