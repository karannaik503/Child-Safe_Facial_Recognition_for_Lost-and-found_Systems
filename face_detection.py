import cv2
import numpy as np
import os
import traceback
import logging
import time
from ultralytics import YOLO

class FaceDetector:
    def __init__(self, model_path=None):
        """
        Initialize face detector with comprehensive logging
        """
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        self.weights_dir = "weights"
        
        # Determine model path
        if model_path is None:
            model_path = os.path.join(self.weights_dir, "yolov8s-widerface.pt")
        
        # Validate model file exists
        if not os.path.exists(model_path):
            self.logger.error(f"Model file not found at {model_path}")
            raise FileNotFoundError(f"Model file not found at {model_path}. Please download the YOLOv8 face detection model.")
        
        try:
            self.model = YOLO(model_path)
            self.logger.info("Face detection model loaded successfully!")
        except Exception as e:
            self.logger.error(f"Error loading face detection model: {e}")
            raise

    def detect_faces_in_image(self, image_path_or_array):
        """
        Detect faces with comprehensive diagnostics
        
        Args:
            image_path_or_array (str or numpy.ndarray): Image source
        
        Returns:
            list: Detected face images
        """
        try:
            # Handle both file path and numpy array input
            if isinstance(image_path_or_array, str):
                image = cv2.imread(image_path_or_array)
                if image is None:
                    self.logger.error(f"Could not read image at {image_path_or_array}")
                    return []
            else:
                image = image_path_or_array

            # Diagnostic image information
            self.logger.info(f"Image shape: {image.shape}")
            self.logger.info(f"Image dtype: {image.dtype}")

            # Run detection
            results = self.model(image)
            
            faces = []
            for r in results:
                boxes = r.boxes
                self.logger.info(f"Number of detected boxes: {len(boxes)}")
                
                for box in boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    
                    # Additional validation
                    if x2 <= x1 or y2 <= y1:
                        self.logger.warning("Invalid bounding box coordinates")
                        continue
                    
                    face = image[y1:y2, x1:x2]
                    
                    if face.size > 0:
                        # Resize face consistently
                        face = cv2.resize(face, (160, 160))
                        faces.append(face)
                        
                        # Log face extraction details
                        self.logger.info(f"Extracted face: {face.shape}")
            
            self.logger.info(f"Total faces detected: {len(faces)}")
            return faces
        
        except Exception as e:
            self.logger.error(f"Face detection error: {e}")
            self.logger.error(traceback.format_exc())
            return []
            
    def detect_faces_in_webcam(self, duration=0, similarity_callback=None):
        """
        Detect faces from webcam feed with real-time processing
        
        Args:
            duration (int): Duration in seconds to run the webcam (0 for indefinite)
            similarity_callback (function): Callback function for processing detected faces
                Expected signature: callback(face) -> None
        
        Returns:
            list: All detected face images during the session
        """
        try:
            # Initialize webcam
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                self.logger.error("Could not open webcam")
                print("Error: Could not open webcam.")
                return []
            
            # Set webcam properties for better performance
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            print("Webcam started. Press 'q' to quit, 's' to save and process the current frame.")
            
            # Variables for session control
            start_time = time.time()
            all_detected_faces = []
            process_this_frame = True
            last_processed_time = time.time()
            processing_interval = 0.5  # Process every half second to reduce CPU load
            
            while True:
                # Check if duration has been reached
                if duration > 0 and (time.time() - start_time) > duration:
                    self.logger.info(f"Webcam session completed ({duration} seconds)")
                    break
                
                # Read frame from webcam
                ret, frame = cap.read()
                
                if not ret:
                    self.logger.error("Failed to capture frame from webcam")
                    break
                
                # Create a copy for display
                display_frame = frame.copy()
                
                # Process at regular intervals to reduce CPU usage
                current_time = time.time()
                if current_time - last_processed_time >= processing_interval:
                    process_this_frame = True
                    last_processed_time = current_time
                
                # Visual indicator for when processing occurs
                cv2.putText(
                    display_frame,
                    "Processing" if process_this_frame else "Standby",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0) if process_this_frame else (0, 0, 255),
                    2
                )
                
                # Process frame for face detection
                if process_this_frame:
                    # Detect faces in current frame
                    faces = self.detect_faces_in_image(frame)
                    
                    if faces:
                        # Add to collection of all faces
                        all_detected_faces.extend(faces)
                        
                        # Display count of detected faces
                        cv2.putText(
                            display_frame,
                            f"Detected: {len(faces)} faces",
                            (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.8,
                            (0, 255, 0),
                            2
                        )
                        
                        # Process each face with callback if provided
                        if similarity_callback:
                            for face in faces:
                                similarity_callback(face, display_frame)
                    
                    process_this_frame = False
                
                # Display the frame
                cv2.imshow('Webcam - Face Detection', display_frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q'):
                    self.logger.info("User quit webcam session")
                    break
                elif key == ord('s'):
                    # Save the current frame for processing
                    save_path = f"captured_frame_{int(time.time())}.jpg"
                    cv2.imwrite(save_path, frame)
                    print(f"Saved current frame to {save_path}")
                    
                    # Force processing on this frame
                    process_this_frame = True
            
            # Release resources
            cap.release()
            cv2.destroyAllWindows()
            
            self.logger.info(f"Webcam session completed with {len(all_detected_faces)} total faces detected")
            return all_detected_faces
            
        except Exception as e:
            self.logger.error(f"Webcam face detection error: {e}")
            self.logger.error(traceback.format_exc())
            return []

def detect_faces(input_path, is_video=False, is_webcam=False, output_path=None, webcam_duration=0, 
                similarity_callback=None):
    """
    Unified face detection function with enhanced logging and webcam support
    
    Args:
        input_path (str): Path to image or video file (ignored for webcam)
        is_video (bool): Whether input is a video
        is_webcam (bool): Whether to use webcam as input
        output_path (str, optional): Path to save output video
        webcam_duration (int): Duration in seconds for webcam (0 for indefinite)
        similarity_callback (function): Callback for processing detected faces
        
    Returns:
        list: Detected face images
    """
    detector = FaceDetector()
    
    if is_webcam:
        # Webcam processing
        logging.info("Starting webcam detection")
        return detector.detect_faces_in_webcam(webcam_duration, similarity_callback)
    elif is_video:
        # Video processing
        faces = []
        cap = cv2.VideoCapture(input_path)
        
        if not cap.isOpened():
            logging.error(f"Could not open video file: {input_path}")
            return []
        
        # Process multiple frames
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = frame_count / fps
        
        logging.info(f"Video details - Frames: {frame_count}, FPS: {fps}, Duration: {duration} seconds")
        
        # Sample frames (every second)
        sample_interval = max(1, int(fps))
        
        for frame_idx in range(0, frame_count, sample_interval):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            
            if not ret:
                break
            
            frame_faces = detector.detect_faces_in_image(frame)
            faces.extend(frame_faces)
        
        cap.release()
        return faces
    else:
        # Image processing
        return detector.detect_faces_in_image(input_path)