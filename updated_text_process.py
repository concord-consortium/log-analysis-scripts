import json
import pandas as pd
import argparse
from difflib import SequenceMatcher

def extract_text(json_obj):
    """
    Extracts 'text' entries from a nested JSON object.
    
    Handles both dictionaries and lists, ensuring that any nested 'text' 
    fields are collected and returned as a list.
    """
    if isinstance(json_obj, dict):
        if 'text' in json_obj and isinstance(json_obj['text'], str):
            return [json_obj['text']]  # If the dictionary contains a text field, extract it
        return [text for value in json_obj.values() for text in extract_text(value)]  # Extract text from dictionary values
    elif isinstance(json_obj, list):
        return [text for item in json_obj for text in extract_text(item)]  # Extract text from lists
    return []  # If not a dict or list, return an empty list

def text_change_text(row):
    """
    Extracts text from 'TEXT_TOOL_CHANGE' events along with its associated tileId.

    Returns:
        - The extracted student-entered text.
        - The tileId associated with the text (if available).
    """
    try:
        parameters = json.loads(row['parameters'])  # Load the parameters field as JSON
        
        # Ensure the event type is 'TEXT_TOOL_CHANGE' and check for 'args'
        if row['event'] == 'TEXT_TOOL_CHANGE' and isinstance(parameters.get('args'), list):
            if isinstance(parameters['args'][0].get('text'), list):  
                return '', parameters.get('tileId', '')  # Return empty text if it's stored as a list (avoid errors)
            return parameters['args'][0].get('text', ''), parameters.get('tileId', '')  # Return extracted text and tileId
        
    except (json.JSONDecodeError, KeyError, TypeError):
        pass  # Safely handle cases where JSON is invalid or missing expected fields
    
    return '', ''  # Default return values if extraction fails

def copy_tile_text(row):
    """
    Extracts copied text from 'COPY_TILE' events and associates it with the tileId.

    Returns:
        - The extracted copied text.
        - The tileId associated with the copied text.
    """
    try:
        parameters = json.loads(row['parameters'])  # Load JSON data
        
        if row['event'] == 'COPY_TILE':  # Check if the event is 'COPY_TILE'
            serialized_object = parameters.get('serializedObject', {})  # Get the copied object's data
            
            # Ensure copied tile contains text and is of type 'Text'
            if serialized_object.get('type') == 'Text' and 'text' in serialized_object:
                extracted_text = serialized_object['text']
                return extracted_text, parameters.get('tileId', '')  # Return copied text and tileId
        
    except (json.JSONDecodeError, KeyError, TypeError):
        pass  # Handle unexpected JSON parsing errors
    
    return '', ''  # Default return values if extraction fails

def combine_text(text_change_content):
    """
    Extracts and combines all 'text' entries from a JSON field containing text change data.

    Returns:
        - A concatenated string of extracted text.
    """
    try:
        parsed_content = json.loads(text_change_content)  # Parse the JSON data
        extracted_texts = extract_text(parsed_content)  # Extract text from the nested structure
        return ' '.join(extracted_texts).strip()  # Join all extracted text into a single string
    except (json.JSONDecodeError, TypeError):
        pass  # Handle cases where JSON is invalid or missing
    return ''  # Default return if extraction fails

def clean_copied_text(copied_text):
    """
    Extracts and cleans copied text from JSON format.

    Returns:
        - A cleaned, concatenated string of copied text.
    """
    try:
        parsed_content = json.loads(copied_text)  # Parse copied text JSON
        extracted_texts = extract_text(parsed_content)  # Extract text
        return ' '.join(extracted_texts).strip()  # Join all text entries
    except (json.JSONDecodeError, TypeError):
        pass  # Handle errors
    return ''  # Default return if extraction fails

def remove_copied_text(student_text, copied_text):
    """
    Uses difflib to remove copied portions from the student's text.

    This function compares the copied text with the student text and removes
    sections that are exact matches.

    Returns:
        - Student text with copied portions removed.
    """
    if not copied_text or not student_text:
        return student_text  # If either text is empty, return original student text
    
    matcher = SequenceMatcher(None, copied_text, student_text)  # Compare copied vs. student text (Difflib)
    result = []
    
    for tag, _, _, j1, j2 in matcher.get_opcodes(): #Difflib (I am not super familiar with difflib so maybe the issue lies here? Or it is just some fault in the logic?)
        if tag in ('insert', 'replace'):  # Keep only the newly inserted or modified parts
            result.append(student_text[j1:j2])
    
    return ''.join(result).strip()  # Return cleaned text with copied portions removed

def compute_student_text(row, copy_dict):
    """
    Removes copied text from student text based on a mapping of tileId to copied text.

    Ensures only the copied text that matches a specific tile is removed.

    Returns:
        - Cleaned student-only text.
    """
    tile_id = row['tileId']  # Get the tile ID
    copied_text = copy_dict.get(tile_id, '')  # Find copied text for this tile
    
    student_text = row['combined_text']  # Get the student's written text
    cleaned_text = remove_copied_text(student_text, copied_text)  # Remove copied portions

    return cleaned_text  # Return cleaned student-only text

def process_student_logs(input_file, output_file):
    """
    Processes student logs to extract, clean, and remove copied text.

    Steps:
        1. Extract text changes (TEXT_TOOL_CHANGE).
        2. Extract copied text (COPY_TILE).
        3. Map copied text to tile IDs.
        4. Remove copied portions from student text.
        5. Save the cleaned data to a CSV file.
    """
    df = pd.read_csv(input_file)  # Load CSV file
    
    # Extract text changes and associated tileId
    df[['text_change', 'text_tileId']] = df.apply(lambda row: pd.Series(text_change_text(row)), axis=1)
    
    # Extract copied text and tileId from COPY_TILE events
    df[['copied_text', 'copy_tileId']] = df.apply(lambda row: pd.Series(copy_tile_text(row)), axis=1)
    
    # Create a dictionary mapping copy_tileId to copied text
    copy_dict = df.set_index('copy_tileId')['copied_text'].dropna().to_dict()

    # Combine extracted text change content into a single string
    df['combined_text'] = df['text_change'].apply(combine_text)

    # Clean extracted copied text
    df['cleaned_copied_text'] = df['copied_text'].apply(clean_copied_text)

    # Remove copied text from student responses
    df['student_only_text'] = df.apply(lambda row: compute_student_text(row, copy_dict), axis=1)
    
    # Match tile IDs to pair related student and copied text
    df_matched_pairs = df.merge(df, left_on='tileId', right_on='copy_tileId', suffixes=('_text_change', '_copied'))
    df_matched_pairs = df_matched_pairs[['tileId_text_change', 'combined_text_text_change', 'cleaned_copied_text_copied', 'student_only_text_text_change']]
    df_matched_pairs.columns = ['Matching Tile ID', 'Student Edited Text', 'Copied Text', 'Final Student-Only Text']
    
    # Save processed data
    df_matched_pairs.to_csv(output_file, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process student logs to extract and clean text while removing copied portions.")
    parser.add_argument("input_file", help="Path to the input CSV file.")
    parser.add_argument("output_file", help="Path to save the processed CSV file.")
    args = parser.parse_args()
    
    process_student_logs(args.input_file, args.output_file)
