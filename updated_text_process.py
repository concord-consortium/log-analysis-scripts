import json
import pandas as pd
import argparse
from difflib import SequenceMatcher

def extract_text(json_obj):
    """Recursively extract 'text' entries from a JSON-like structure.

    Handles both dictionaries and lists by traversing nested structures.
    """
    if isinstance(json_obj, dict):
        if 'text' in json_obj and isinstance(json_obj['text'], str):
            return [json_obj['text']]
        # Recursively process all dictionary values
        return [text for value in json_obj.values() for text in extract_text(value)]
    elif isinstance(json_obj, list):
        # Recursively process all list elements
        return [text for item in json_obj for text in extract_text(item)]
    return []

def text_change_text(row):
    """Extract raw text-change-related data from the 'parameters' column.

    Returns:
        - Extracted text (if available)
        - Associated tile ID (if applicable)
    """
    try:
        parameters = json.loads(row['parameters'])
        
        # Ensure event type is TEXT_TOOL_CHANGE and check for args
        if row['event'] == 'TEXT_TOOL_CHANGE' and isinstance(parameters.get('args'), list):
            # Handle cases where text is a list (avoid processing incorrectly)
            if isinstance(parameters['args'][0].get('text'), list):
                return '', parameters.get('tileId', '')
            return parameters['args'][0].get('text', ''), parameters.get('tileId', '')
        
    except (json.JSONDecodeError, KeyError, TypeError):
        pass  # Safely handle missing or malformed JSON
    
    return '', ''

def copy_tile_text(row):
    """Extract copied text and tileId from COPY_TILE events, ensuring the tile is text-based.

    Returns:
        - Extracted copied text
        - Tile ID (if applicable)
    """
    try:
        parameters = json.loads(row['parameters'])
        
        if row['event'] == 'COPY_TILE':
            serialized_object = parameters.get('serializedObject', {})
            
            # Ensure copied tile is a text tile before extracting
            if serialized_object.get('type') == 'Text' and 'text' in serialized_object:
                extracted_text = serialized_object['text']
                return extracted_text, parameters.get('tileId', '')
        
    except (json.JSONDecodeError, KeyError, TypeError):
        pass  # Handle unexpected JSON errors safely
    
    return '', ''

def combine_text(text_change_content):
    """Extract and combine all 'text' entries from a text_change_text JSON field.

    Returns:
        - A concatenated string of extracted text
    """
    try:
        parsed_content = json.loads(text_change_content)
        extracted_texts = extract_text(parsed_content)
        return ' '.join(extracted_texts).strip()
    except (json.JSONDecodeError, TypeError):
        pass  # Handle cases where content is not valid JSON
    return ''

def clean_copied_text(copied_text):
    """Extract and clean copied text from JSON format.

    Returns:
        - A cleaned, concatenated string of copied text.
    """
    try:
        parsed_content = json.loads(copied_text)
        extracted_texts = extract_text(parsed_content)
        return ' '.join(extracted_texts).strip()
    except (json.JSONDecodeError, TypeError):
        pass
    return ''

def remove_copied_text(student_text, copied_text):
    """Use difflib to remove copied portions from student text.

    Returns:
        - Student text with copied sections removed.
    """
    if not copied_text or not student_text:
        return student_text  # No changes needed if one of the texts is empty
    
    matcher = SequenceMatcher(None, copied_text, student_text)
    result = []
    
    for tag, _, _, j1, j2 in matcher.get_opcodes():
        if tag in ('insert', 'replace'):  # Keep only new student text
            result.append(student_text[j1:j2])
    
    return ''.join(result).strip()

def compute_student_text(row, copy_dict):
    """Remove copied text from student text based on tile ID mapping.

    Ensures only the copied text matching a specific tile is removed.
    """
    tile_id = row['tileId']
    copied_text = copy_dict.get(tile_id, '')

    student_text = row['combined_text']
    cleaned_text = remove_copied_text(student_text, copied_text)

    return cleaned_text

def process_student_logs(input_file, output_file):
    """Processes student logs to extract and clean text while removing copied portions."""
    df = pd.read_csv(input_file)
    
    # Extract text change and associated tile ID
    df[['text_change', 'text_tileId']] = df.apply(lambda row: pd.Series(text_change_text(row)), axis=1)
    
    # Extract copied text and tile ID from COPY_TILE events
    df[['copied_text', 'copy_tileId']] = df.apply(lambda row: pd.Series(copy_tile_text(row)), axis=1)
    copy_dict = df.set_index('copy_tileId')['copied_text'].dropna().to_dict()

    # Combine extracted text change content
    df['combined_text'] = df['text_change'].apply(combine_text)

    # Clean extracted copied text
    df['cleaned_copied_text'] = df['copied_text'].apply(clean_copied_text)

    # Remove copied text from student text
    df['student_only_text'] = df.apply(lambda row: compute_student_text(row, copy_dict), axis=1)
    
    # Match tile IDs to pair related student and copied text
    df_matched_pairs = df.merge(df, left_on='tileId', right_on='copy_tileId', suffixes=('_text_change', '_copied'))
    df_matched_pairs = df_matched_pairs[['tileId_text_change', 'combined_text_text_change', 'cleaned_copied_text_copied', 'student_only_text_text_change']]
    df_matched_pairs.columns = ['Matching Tile ID', 'Student Edited Text', 'Copied Text', 'Final Student-Only Text']
    
    df_matched_pairs.to_csv(output_file, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process student logs to extract and clean text while removing copied portions.")
    parser.add_argument("input_file", help="Path to the input CSV file.")
    parser.add_argument("output_file", help="Path to save the processed CSV file.")
    args = parser.parse_args()
    
    process_student_logs(args.input_file, args.output_file)
