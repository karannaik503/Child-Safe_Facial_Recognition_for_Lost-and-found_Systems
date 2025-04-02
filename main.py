import sys
import os
from face_detection import detect_faces
from embeddings import extract_embedding
from vector_store import add_embedding_to_faiss, search_faiss
from database import (
    insert_child_metadata, 
    create_metadata_table, 
    get_child_by_embedding_id,
    update_case_status
)
from storage import store_encrypted_image
import numpy as np
import logging
import cv2
from config import SIMILARITY_THRESHOLD

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

def register_lost_child(image_url, name, age, gender, guardian_contact):
    """
    Register a lost child with comprehensive logging and error handling
    
    Args:
        image_url (str): Path to child's image
        name (str): Child's name
        age (int): Child's age
        gender (str): Child's gender
        guardian_contact (str): Guardian's contact info
    """
    logging.info(f"Registering lost child: {name}")
    
    # Detect faces
    faces = detect_faces(image_url)
    
    if not faces:
        logging.error("No face detected in the image")
        print("No face detected.")
        return
    
    # Use the first detected face
    face = faces[0]
    
    # Extract embedding
    embedding = extract_embedding(face)
    
    if embedding is None:
        logging.error("Failed to extract embedding")
        print("Failed to extract facial embedding.")
        return
    
    # Generate unique embedding ID (use hash for consistency)
    embedding_id = hash(name + str(age) + str(np.mean(embedding))) % 1000000
    
    logging.info(f"Generated Embedding ID: {embedding_id}")
    
    # Add embedding to vector store
    if not add_embedding_to_faiss(embedding, embedding_id):
        logging.error("Failed to add embedding to vector store")
        print("Error adding embedding to database.")
        return
    
    # Store encrypted image
    try:
        encrypted_image_path = store_encrypted_image(image_url, embedding_id)
        
        # Insert metadata
        metadata_id = insert_child_metadata(
            name, age, gender, guardian_contact, 
            embedding_id, encrypted_image_path
        )
        
        if metadata_id:
            logging.info(f"Child registered successfully. Metadata ID: {metadata_id}")
            print(f"Child registered successfully with Embedding ID: {embedding_id}")
        else:
            logging.error("Failed to insert child metadata")
            print("Error registering child.")
    
    except Exception as e:
        logging.error(f"Registration error: {e}")
        print("An error occurred during registration.")

def close_child_case(embedding_id):
    """
    Close a child's case with comprehensive error handling
    """
    try:
        # Update case status to Closed
        if update_case_status(embedding_id):
            logging.info(f"Case for Embedding ID {embedding_id} closed successfully")
            print(f"Case for Embedding ID {embedding_id} has been closed successfully.")
            return True
        else:
            logging.error(f"Failed to close case for Embedding ID {embedding_id}")
            print(f"Failed to close case for Embedding ID {embedding_id}")
            return False
    except Exception as e:
        logging.error(f"Error closing case: {e}")
        print(f"Error closing case: {e}")
        return False

def process_face_for_match(face, display_frame=None):
    """
    Process a face and find matches - used as a callback for webcam processing
    
    Args:
        face (numpy.ndarray): Detected face image
        display_frame (numpy.ndarray, optional): Frame for displaying match info
    
    Returns:
        list: List of matching embedding IDs
    """
    # Extract embedding
    embedding = extract_embedding(face)
    
    if embedding is None:
        return []
    
    # Search for matches
    matches = search_faiss(embedding, top_k=5, similarity_threshold=SIMILARITY_THRESHOLD)
    
    if matches[0] != -1 and display_frame is not None:
        # Display match info on frame
        for i, embedding_id in enumerate(matches[:3]):  # Limit to top 3 for display
            embedding_id = int(embedding_id)
            child_details = get_child_by_embedding_id(embedding_id)
            
            if child_details:
                # Display match on frame
                text = f"Match #{i+1}: {child_details['name']}, ID: {embedding_id}"
                y_pos = 90 + (i * 30)  # Position text entries vertically
                cv2.putText(
                    display_frame,
                    text,
                    (10, y_pos),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 0, 0),
                    2
                )
    
    return matches if matches[0] != -1 else []

def identify_found_child(input_path, is_video=False, is_webcam=False, output_video_path=None):
    """
    Identify a found child from image, video, or webcam with comprehensive logging
    
    Args:
        input_path (str): Path to image or video (ignored for webcam)
        is_video (bool): Whether input is a video
        is_webcam (bool): Whether to use webcam for input
        output_video_path (str, optional): Path to save output video
    """
    logging.info(f"Identifying child from {'webcam' if is_webcam else ('video: ' + input_path if is_video else 'image: ' + input_path)}")
    
    # Set up the similarity callback for webcam mode
    similarity_callback = process_face_for_match if is_webcam else None
    
    # Detect faces
    faces = detect_faces(
        input_path, 
        is_video=is_video, 
        is_webcam=is_webcam, 
        output_path=output_video_path,
        similarity_callback=similarity_callback
    )
    
    if not faces:
        logging.warning("No faces detected in the input")
        print("No faces detected.")
        return
    
    # Unique matches tracking
    unique_matches = set()
    
    # Process each detected face
    for i, face in enumerate(faces, 1):
        logging.info(f"Processing face {i}/{len(faces)}")
        
        # Extract embedding
        embedding = extract_embedding(face)
        
        if embedding is None:
            logging.warning(f"Failed to extract embedding for face {i}")
            continue
        
        # Search for matches
        matches = search_faiss(embedding, top_k=5, similarity_threshold=SIMILARITY_THRESHOLD)
        
        if matches[0] != -1:
            # Add matches to the unique set
            unique_matches.update(matches)
    
    if unique_matches:
        print("Potential matches found!")
        
        # Convert to list and sort for consistent output
        sorted_matches = sorted(list(unique_matches))
        
        # Track already printed child IDs
        printed_child_ids = set()
        
        for embedding_id in sorted_matches:
            # Convert numpy.int64 to regular integer
            embedding_id = int(embedding_id)
            
            # Retrieve child details
            child_details = get_child_by_embedding_id(embedding_id)
            
            if child_details:
                # Check if this child ID has already been printed
                if child_details['child_id'] not in printed_child_ids:
                    print("\nChild Details:")
                    print(f"Child ID: {child_details['child_id']}")
                    print(f"Embedding ID: {embedding_id}")
                    print(f"Name: {child_details['name']}")
                    print(f"Age: {child_details['age']}")
                    print(f"Gender: {child_details['gender']}")
                    print(f"Guardian Contact: {child_details['guardian_contact']}")
                    print(f"Case Status: {child_details['case_status']}")
                    
                    # Prompt to close the case
                    close_case = input("Is this the correct child? Do you want to close this case? (yes/no): ").lower()
                    if close_case in ['yes', 'y']:
                        close_child_case(embedding_id)
                    
                    # Add to printed child IDs to prevent duplicates
                    printed_child_ids.add(child_details['child_id'])
            else:
                logging.warning(f"No details found for Embedding ID: {embedding_id}")
    else:
        logging.info("No matches found in the entire process")
        print("No matches found.")

def main():
    """
    Comprehensive main execution with enhanced error handling and webcam support
    """
    # Configure comprehensive logging
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('child_recognition.log')
        ]
    )
    
    if len(sys.argv) < 2:
        logging.error("Insufficient arguments")
        print("Usage: python main.py [register/identify/webcam/close] [args...]")
        print("\nExamples:")
        print("  Register: python main.py register image_path name age gender guardian_contact")
        print("  Identify from image: python main.py identify image_path")
        print("  Identify from video: python main.py identify video_path --video")
        print("  Identify from webcam: python main.py webcam")
        print("  Close case: python main.py close embedding_id")
        sys.exit(1)
    
    action = sys.argv[1]
    
    try:
        if action == "register":
            # Expect: python main.py register image_path name age gender guardian_contact
            if len(sys.argv) != 7:
                logging.error("Incorrect arguments for registration")
                print("Register requires: image_path name age gender guardian_contact")
                sys.exit(1)
            
            input_path = sys.argv[2]
            name, age, gender, guardian_contact = sys.argv[3:7]
            register_lost_child(input_path, name, int(age), gender, guardian_contact)
        
        elif action == "identify":
            # Expect at least: python main.py identify input_path [--video]
            if len(sys.argv) < 3:
                logging.error("Insufficient arguments for identification")
                print("Identify requires an input path (image or video)")
                sys.exit(1)
            
            input_path = sys.argv[2]
            is_video = "--video" in sys.argv or input_path.lower().endswith(('.mp4', '.avi', '.mov'))
            
            # Optional output path for video
            output_video_path = None
            if is_video:
                output_video_path = input_path.replace('.', '_detected.')
            
            identify_found_child(input_path, is_video=is_video, is_webcam=False, output_video_path=output_video_path)
        
        elif action == "webcam":
            # Webcam identification: python main.py webcam
            identify_found_child(None, is_video=False, is_webcam=True)
        
        elif action == "close":
            # Close a specific case: python main.py close embedding_id
            if len(sys.argv) != 3:
                logging.error("Incorrect arguments for case closure")
                print("Close requires an Embedding ID")
                sys.exit(1)
            
            embedding_id = int(sys.argv[2])
            close_child_case(embedding_id)
        
        else:
            logging.error("Invalid action specified")
            print("Invalid action. Use 'register', 'identify', 'webcam', or 'close'")
            sys.exit(1)
    
    except Exception as e:
        logging.critical(f"Unhandled exception in main: {e}")
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()