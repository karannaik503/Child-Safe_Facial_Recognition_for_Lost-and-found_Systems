import cv2
import argparse
from ultralytics import YOLO
import time
import os

def parse_arguments():
    parser = argparse.ArgumentParser(description='YOLOv8 Face Detection with GUI')
    parser.add_argument('--model', type=str, default='face_detection.pt', 
                        help='Path to the trained YOLOv8 model file (.pt)')
    parser.add_argument('--conf', type=float, default=0.5, 
                        help='Confidence threshold for detections')
    parser.add_argument('--device', type=str, default='0', 
                        help='Device to use (webcam index, usually 0 for built-in webcam)')
    parser.add_argument('--save', action='store_true',
                        help='Save output frames instead of just displaying them')
    parser.add_argument('--output', type=str, default='output',
                        help='Output folder for saved frames')
    return parser.parse_args()

def main():
    # Parse command-line arguments
    args = parse_arguments()
    
    # Create output directory if saving frames
    if args.save:
        os.makedirs(args.output, exist_ok=True)
        print(f"Saving output frames to {args.output}/")
    
    # Load the YOLOv8 model
    print(f"Loading model from {args.model}...")
    model = YOLO(args.model)
    
    # Open the webcam
    print(f"Opening webcam device {args.device}...")
    try:
        cap = cv2.VideoCapture(int(args.device))
    except:
        cap = cv2.VideoCapture(args.device)  # If the device is a path to a video file
    
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return
    
    # Get webcam properties
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"Webcam resolution: {frame_width}x{frame_height}, FPS: {fps}")
    
    if not args.save:
        print("Press 'q' to quit the GUI")
    
    # Create video writer if saving frames
    if args.save:
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(os.path.join(args.output, 'output.avi'), 
                             fourcc, 20.0, (frame_width, frame_height))
    
    # Initialize FPS calculation variables
    prev_time = time.time()
    frame_count = 0
    frame_index = 0
    
    try:
        while True:
            # Read a frame from the webcam
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to capture frame from webcam.")
                break
            
            # Perform face detection
            results = model(frame, conf=args.conf, verbose=False)
            
            # Process detections
            if results and len(results) > 0:
                result = results[0]  # Get the first result
                annotated_frame = result.plot()  # Draw bounding boxes
                
                # Calculate and display FPS
                frame_count += 1
                current_time = time.time()
                elapsed_time = current_time - prev_time
                
                if elapsed_time >= 1.0:  # Update FPS every second
                    fps = frame_count / elapsed_time
                    frame_count = 0
                    prev_time = current_time
                
                # Display FPS on the frame
                cv2.putText(annotated_frame, f"FPS: {fps:.1f}", (20, 40), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:
                annotated_frame = frame  # If no detections, use original frame
            
            # Save every 100th frame if saving is enabled
            if args.save:
                out.write(annotated_frame)  # Save all frames to video
                
                if frame_index % 100 == 0:
                    cv2.imwrite(os.path.join(args.output, f'frame_{frame_index:04d}.jpg'), annotated_frame)
                    print(f"Saved frame {frame_index:04d}.jpg")
                
                frame_index += 1
            
            # Show the GUI with real-time detection
            cv2.imshow("YOLOv8 Face Detection", annotated_frame)
            
            # Exit if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            # Allow user to terminate with Ctrl+C in save mode
            if args.save and frame_index % 100 == 0:
                print("Press Ctrl+C to terminate...")
    
    except KeyboardInterrupt:
        print("Process interrupted by user.")
    
    finally:
        # Release resources
        cap.release()
        if args.save:
            out.release()
        cv2.destroyAllWindows()
        print("Face detection terminated.")

if __name__ == "__main__":
    main()


#!Python run script
#to run the gui
#python testing_live_webcam.py --model weights/yolov8s-widerface.pt --conf 0.5 --device 0
#to save the webcam image every at 100th frame
#python testing_live_webcam.py --model weights/yolov8s-widerface.pt --conf 0.5 --device 0 --save --output webcam_outputs