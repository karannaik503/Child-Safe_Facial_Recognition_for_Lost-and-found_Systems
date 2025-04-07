# import pywhatkit
# import logging
# import time
# import webbrowser
# from urllib.parse import quote
# import random
# import os
# from twilio.rest import Client
# import threading

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)

# class GuardianNotifier:
#     def __init__(self):
#         """Initialize the notification system"""
#         self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
#         self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
#         self.twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        
#         # Initialize Twilio client if credentials are available
#         self.twilio_client = None
#         if all([self.twilio_account_sid, self.twilio_auth_token, self.twilio_phone_number]):
#             try:
#                 self.twilio_client = Client(self.twilio_account_sid, self.twilio_auth_token)
#                 logger.info("Twilio client initialized successfully")
#             except Exception as e:
#                 logger.error(f"Failed to initialize Twilio client: {e}")
    
#     def clean_phone_number(self, phone_number):
#         """
#         Clean and format phone number for WhatsApp
        
#         Args:
#             phone_number (str): Raw phone number
            
#         Returns:
#             str: Cleaned phone number (with country code if needed)
#         """
#         # Remove any non-digit characters
#         cleaned = ''.join(filter(str.isdigit, phone_number))
        
#         # Ensure there's a country code
#         if not cleaned.startswith('+'):
#             # If number starts with 0, replace with country code
#             if cleaned.startswith('0'):
#                 cleaned = '+91' + cleaned[1:]  # Default to India (+91)
#             # If no country code and doesn't start with 0, assume it's a local number
#             elif len(cleaned) == 10:  # Standard length for local numbers
#                 cleaned = '+91' + cleaned  # Default to India (+91)
        
#         return cleaned
    
#     def notify_multiple_guardians(phone_numbers, child_name, found_location=None, custom_message=None):
#         """
#         Notify multiple guardians for the same child
        
#         Args:
#             phone_numbers (list): List of guardian phone numbers
#             child_name (str): Child's name
#             found_location (str, optional): Where the child was found
#             custom_message (str, optional): Custom message to add
            
#         Returns:
#             dict: Dictionary mapping phone numbers to (success_bool, method_used)
#         """
#         notifier = GuardianNotifier()
#         results = {}
        
#         for phone_number in phone_numbers:
#             result, method = notifier.notify_guardian(phone_number, child_name, 
#                                                     found_location, custom_message)
#             results[phone_number] = (result, method)
        
#         return results


#     def notify_multiple_guardians_async(phone_numbers, child_name, found_location=None, 
#                                     custom_message=None, callback=None):
#         """
#         Notify multiple guardians asynchronously
        
#         Args:
#             phone_numbers (list): List of guardian phone numbers
#             child_name (str): Child's name
#             found_location (str, optional): Where the child was found
#             custom_message (str, optional): Custom message to add
#             callback (function, optional): Function to call after all notifications are sent
#                 Callback signature: callback(results_dict)
#         """
#     def _notify_thread():
#             results = {}
#             for phone_number in phone_numbers:
#                 notifier = GuardianNotifier()
#                 result, method = notifier.notify_guardian(
#                     phone_number, child_name, found_location, custom_message
#                 )
#                 results[phone_number] = (result, method)
            
#             if callback:
#                 callback(results)
        
#         # Start notification in a separate thread to avoid blocking GUI
#         thread = threading.Thread(target=_notify_thread)
#         thread.daemon = True
#         thread.start()
        
#         return thread
#     def send_whatsapp_message_pywhatkit(self, phone_number, message, child_name, location_found=None):
#         """
#         Send WhatsApp message using pywhatkit
        
#         Args:
#             phone_number (str): Guardian's phone number
#             message (str): Message content
#             child_name (str): Name of the child
#             location_found (str, optional): Where the child was found
            
#         Returns:
#             bool: True if successful, False otherwise
#         """
#         try:
#             # Clean phone number
#             cleaned_number = self.clean_phone_number(phone_number)
#             if cleaned_number.startswith('+'):
#                 cleaned_number = cleaned_number[1:]  # Remove + for pywhatkit
                
#             # Format the message
#             full_message = f"CHILD SAFETY ALERT: {child_name} has been found"
#             if location_found:
#                 full_message += f" at {location_found}"
#             full_message += f". {message}"
            
#             # Get current time + 2 minutes (pywhatkit needs some buffer time)
#             current_time = time.localtime()
#             hour = current_time.tm_hour
#             minute = current_time.tm_min + 2
            
#             # Handle minute overflow
#             if minute >= 60:
#                 hour = (hour + 1) % 24
#                 minute = minute % 60
            
#             # Send message through pywhatkit
#             pywhatkit.sendwhatmsg(cleaned_number, full_message, hour, minute, wait_time=20, tab_close=True)
#             logger.info(f"WhatsApp message sent to {cleaned_number} using pywhatkit")
#             return True
            
#         except Exception as e:
#             logger.error(f"Failed to send WhatsApp message via pywhatkit: {e}")
#             return False
    
#     def send_whatsapp_direct_link(self, phone_number, message, child_name, location_found=None):
#         """
#         Open WhatsApp web with pre-filled message
        
#         Args:
#             phone_number (str): Guardian's phone number
#             message (str): Message content
#             child_name (str): Name of the child
#             location_found (str, optional): Where the child was found
            
#         Returns:
#             bool: True if successful, False otherwise
#         """
#         try:
#             # Clean phone number
#             cleaned_number = self.clean_phone_number(phone_number)
#             if cleaned_number.startswith('+'):
#                 cleaned_number = cleaned_number[1:]  # Remove + for web link
                
#             # Format the message
#             full_message = f"CHILD SAFETY ALERT: {child_name} has been found"
#             if location_found:
#                 full_message += f" at {location_found}"
#             full_message += f". {message}"
            
#             # URL encode the message
#             encoded_message = quote(full_message)
            
#             # Create WhatsApp web link
#             whatsapp_link = f"https://web.whatsapp.com/send?phone={cleaned_number}&text={encoded_message}"
            
#             # Open in browser
#             webbrowser.open(whatsapp_link)
#             logger.info(f"WhatsApp web opened for {cleaned_number}")
#             return True
            
#         except Exception as e:
#             logger.error(f"Failed to open WhatsApp web: {e}")
#             return False
    
#     def send_sms_via_twilio(self, phone_number, message, child_name, location_found=None):
#         """
#         Send SMS via Twilio as a fallback
        
#         Args:
#             phone_number (str): Guardian's phone number
#             message (str): Message content
#             child_name (str): Name of the child
#             location_found (str, optional): Where the child was found
            
#         Returns:
#             bool: True if successful, False otherwise
#         """
#         if not self.twilio_client:
#             logger.error("Twilio client not initialized. Cannot send SMS.")
#             return False
            
#         try:
#             # Clean phone number
#             cleaned_number = self.clean_phone_number(phone_number)
                
#             # Format the message
#             full_message = f"CHILD SAFETY ALERT: {child_name} has been found"
#             if location_found:
#                 full_message += f" at {location_found}"
#             full_message += f". {message}"
            
#             # Send SMS via Twilio
#             message = self.twilio_client.messages.create(
#                 body=full_message,
#                 from_=self.twilio_phone_number,
#                 to=cleaned_number
#             )
            
#             logger.info(f"SMS sent to {cleaned_number} via Twilio. SID: {message.sid}")
#             return True
            
#         except Exception as e:
#             logger.error(f"Failed to send SMS via Twilio: {e}")
#             return False
    
#     def notify_guardian(self, phone_number, child_name, found_location=None, custom_message=None):
#         """
#         Main method to notify guardian with fallbacks
        
#         Args:
#             phone_number (str): Guardian's phone number
#             child_name (str): Child's name
#             found_location (str, optional): Where the child was found
#             custom_message (str, optional): Custom message to add
            
#         Returns:
#             tuple: (success_bool, method_used)
#         """
#         if not phone_number:
#             logger.error("No phone number provided")
#             return False, "error"
            
#         # Default message if none provided
#         if not custom_message:
#             custom_message = "Please contact the authorities immediately to reunite with your child."
        
#         # Add random confirmation code for verification
#         confirmation_code = ''.join(random.choices('0123456789', k=6))
#         full_message = f"{custom_message} Please use confirmation code {confirmation_code} for verification."
        
#         # Try multiple methods in order
        
#         # Method 1: Try pywhatkit (closes after sending)
#         def try_pywhatkit():
#             success = self.send_whatsapp_message_pywhatkit(
#                 phone_number, full_message, child_name, found_location
#             )
#             if success:
#                 return True
#             return False
            
#         # Method 2: Try WhatsApp web direct link
#         def try_direct_link():
#             return self.send_whatsapp_direct_link(
#                 phone_number, full_message, child_name, found_location
#             )
            
#         # Method 3: Try SMS via Twilio
#         def try_sms():
#             if self.twilio_client:
#                 return self.send_sms_via_twilio(
#                     phone_number, full_message, child_name, found_location
#                 )
#             return False
        
#         # Try methods in sequence
#         methods = [
#             ("pywhatkit", try_pywhatkit),
#             ("whatsapp_link", try_direct_link),
#             ("sms", try_sms)
#         ]
        
#         for method_name, method_func in methods:
#             try:
#                 if method_func():
#                     logger.info(f"Successfully notified guardian via {method_name}")
#                     return True, method_name
#             except Exception as e:
#                 logger.error(f"Error using {method_name}: {e}")
#                 continue
                
#         logger.error("All notification methods failed")
#         return False, "all_failed"
    
#     def notify_guardian_async(self, phone_number, child_name, found_location=None, 
#                               custom_message=None, callback=None):
#         """
#         Send notification asynchronously
        
#         Args:
#             phone_number (str): Guardian's phone number
#             child_name (str): Child's name
#             found_location (str, optional): Where the child was found
#             custom_message (str, optional): Custom message to add
#             callback (function, optional): Function to call after completion
#         """
#         def _notify_thread():
#             result, method = self.notify_guardian(
#                 phone_number, child_name, found_location, custom_message
#             )
#             if callback:
#                 callback(result, method)
        
#         # Start notification in a separate thread to avoid blocking GUI
#         thread = threading.Thread(target=_notify_thread)
#         thread.daemon = True
#         thread.start()
        
#         return thread

# # Utility functions for direct use
# def notify_guardian(phone_number, child_name, found_location=None, custom_message=None):
#     """
#     Convenience function to notify guardian
    
#     Args:
#         phone_number (str): Guardian's phone number
#         child_name (str): Child's name
#         found_location (str, optional): Where the child was found
#         custom_message (str, optional): Custom message to add
        
#     Returns:
#         tuple: (success_bool, method_used)
#     """
#     notifier = GuardianNotifier()
#     return notifier.notify_guardian(phone_number, child_name, found_location, custom_message)

# def notify_guardian_async(phone_number, child_name, found_location=None, 
#                          custom_message=None, callback=None):
#     """
#     Convenience function to notify guardian asynchronously
    
#     Args:
#         phone_number (str): Guardian's phone number
#         child_name (str): Child's name
#         found_location (str, optional): Where the child was found
#         custom_message (str, optional): Custom message to add
#         callback (function, optional): Function to call after completion
#     """
#     notifier = GuardianNotifier()
#     return notifier.notify_guardian_async(phone_number, child_name, found_location, 
#                                         custom_message, callback)

# notification.py

import pywhatkit
import logging
import time
import webbrowser
from urllib.parse import quote
import random
import os
from twilio.rest import Client
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GuardianNotifier:
    def __init__(self):
        """Initialize the notification system"""
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_phone_number = os.getenv("TWILIO_PHONE_NUMBER")
        
        # Initialize Twilio client if credentials are available
        self.twilio_client = None
        if all([self.twilio_account_sid, self.twilio_auth_token, self.twilio_phone_number]):
            try:
                self.twilio_client = Client(self.twilio_account_sid, self.twilio_auth_token)
                logger.info("Twilio client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {e}")
    
    def clean_phone_number(self, phone_number):
        """
        Clean and format phone number for WhatsApp
        
        Args:
            phone_number (str): Raw phone number
            
        Returns:
            str: Cleaned phone number (with country code if needed)
        """
        # Remove any non-digit characters
        cleaned = ''.join(filter(str.isdigit, phone_number))
        
        # Ensure there's a country code
        if not cleaned.startswith('+'):
            # If number starts with 0, replace with country code
            if cleaned.startswith('0'):
                cleaned = '+91' + cleaned[1:]  # Default to India (+91)
            # If no country code and doesn't start with 0, assume it's a local number
            elif len(cleaned) == 10:  # Standard length for local numbers
                cleaned = '+91' + cleaned  # Default to India (+91)
        
        return cleaned
    
    def send_whatsapp_message_pywhatkit(self, phone_number, message, child_name, location_found=None):
        """
        Send WhatsApp message using pywhatkit
        
        Args:
            phone_number (str): Guardian's phone number
            message (str): Message content
            child_name (str): Name of the child
            location_found (str, optional): Where the child was found
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Clean phone number
            cleaned_number = self.clean_phone_number(phone_number)
            if cleaned_number.startswith('+'):
                cleaned_number = cleaned_number[1:]  # Remove + for pywhatkit
                
            # Format the message
            full_message = f"CHILD SAFETY ALERT: {child_name} has been found"
            if location_found:
                full_message += f" at {location_found}"
            full_message += f". {message}"
            
            # Get current time + 2 minutes (pywhatkit needs some buffer time)
            current_time = time.localtime()
            hour = current_time.tm_hour
            minute = current_time.tm_min + 2
            
            # Handle minute overflow
            if minute >= 60:
                hour = (hour + 1) % 24
                minute = minute % 60
            
            # Send message through pywhatkit
            pywhatkit.sendwhatmsg(cleaned_number, full_message, hour, minute, wait_time=20, tab_close=True)
            logger.info(f"WhatsApp message sent to {cleaned_number} using pywhatkit")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send WhatsApp message via pywhatkit: {e}")
            return False
    
    def send_whatsapp_direct_link(self, phone_number, message, child_name, location_found=None):
        """
        Open WhatsApp web with pre-filled message
        
        Args:
            phone_number (str): Guardian's phone number
            message (str): Message content
            child_name (str): Name of the child
            location_found (str, optional): Where the child was found
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Clean phone number
            cleaned_number = self.clean_phone_number(phone_number)
            if cleaned_number.startswith('+'):
                cleaned_number = cleaned_number[1:]  # Remove + for web link
                
            # Format the message
            full_message = f"CHILD SAFETY ALERT: {child_name} has been found"
            if location_found:
                full_message += f" at {location_found}"
            full_message += f". {message}"
            
            # URL encode the message
            encoded_message = quote(full_message)
            
            # Create WhatsApp web link
            whatsapp_link = f"https://web.whatsapp.com/send?phone={cleaned_number}&text={encoded_message}"
            
            # Open in browser
            webbrowser.open(whatsapp_link)
            logger.info(f"WhatsApp web opened for {cleaned_number}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to open WhatsApp web: {e}")
            return False
    
    def send_sms_via_twilio(self, phone_number, message, child_name, location_found=None):
        """
        Send SMS via Twilio as a fallback
        
        Args:
            phone_number (str): Guardian's phone number
            message (str): Message content
            child_name (str): Name of the child
            location_found (str, optional): Where the child was found
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.twilio_client:
            logger.error("Twilio client not initialized. Cannot send SMS.")
            return False
            
        try:
            # Clean phone number
            cleaned_number = self.clean_phone_number(phone_number)
                
            # Format the message
            full_message = f"CHILD SAFETY ALERT: {child_name} has been found"
            if location_found:
                full_message += f" at {location_found}"
            full_message += f". {message}"
            
            # Send SMS via Twilio
            message = self.twilio_client.messages.create(
                body=full_message,
                from_=self.twilio_phone_number,
                to=cleaned_number
            )
            
            logger.info(f"SMS sent to {cleaned_number} via Twilio. SID: {message.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send SMS via Twilio: {e}")
            return False
    
    def notify_guardian(self, phone_number, child_name, found_location=None, custom_message=None):
        """
        Main method to notify guardian with fallbacks
        
        Args:
            phone_number (str): Guardian's phone number
            child_name (str): Child's name
            found_location (str, optional): Where the child was found
            custom_message (str, optional): Custom message to add
            
        Returns:
            tuple: (success_bool, method_used)
        """
        if not phone_number:
            logger.error("No phone number provided")
            return False, "error"
            
        # Default message if none provided
        if not custom_message:
            custom_message = "Please contact the authorities immediately to reunite with your child."
        
        # Add random confirmation code for verification
        confirmation_code = ''.join(random.choices('0123456789', k=6))
        full_message = f"{custom_message} Please use confirmation code {confirmation_code} for verification."
        
        # Try multiple methods in order
        
        # Method 1: Try pywhatkit (closes after sending)
        def try_pywhatkit():
            success = self.send_whatsapp_message_pywhatkit(
                phone_number, full_message, child_name, found_location
            )
            if success:
                return True
            return False
            
        # Method 2: Try WhatsApp web direct link
        def try_direct_link():
            return self.send_whatsapp_direct_link(
                phone_number, full_message, child_name, found_location
            )
            
        # Method 3: Try SMS via Twilio
        def try_sms():
            if self.twilio_client:
                return self.send_sms_via_twilio(
                    phone_number, full_message, child_name, found_location
                )
            return False
        
        # Try methods in sequence
        methods = [
            ("pywhatkit", try_pywhatkit),
            ("whatsapp_link", try_direct_link),
            ("sms", try_sms)
        ]
        
        for method_name, method_func in methods:
            try:
                if method_func():
                    logger.info(f"Successfully notified guardian via {method_name}")
                    return True, method_name
            except Exception as e:
                logger.error(f"Error using {method_name}: {e}")
                continue
                
        logger.error("All notification methods failed")
        return False, "all_failed"
    
    def notify_guardian_async(self, phone_number, child_name, found_location=None, 
                              custom_message=None, callback=None):
        """
        Send notification asynchronously
        
        Args:
            phone_number (str): Guardian's phone number
            child_name (str): Child's name
            found_location (str, optional): Where the child was found
            custom_message (str, optional): Custom message to add
            callback (function, optional): Function to call after completion
        """
        def _notify_thread():
            result, method = self.notify_guardian(
                phone_number, child_name, found_location, custom_message
            )
            if callback:
                callback(result, method)
                
        # Start notification in a separate thread to avoid blocking GUI
        thread = threading.Thread(target=_notify_thread)
        thread.daemon = True
        thread.start()
        
        return thread

# Utility functions for direct use
def notify_guardian(phone_number, child_name, found_location=None, custom_message=None):
    """
    Convenience function to notify guardian
    
    Args:
        phone_number (str): Guardian's phone number
        child_name (str): Child's name
        found_location (str, optional): Where the child was found
        custom_message (str, optional): Custom message to add
        
    Returns:
        tuple: (success_bool, method_used)
    """
    notifier = GuardianNotifier()
    return notifier.notify_guardian(phone_number, child_name, found_location, custom_message)

def notify_guardian_async(phone_number, child_name, found_location=None, 
                         custom_message=None, callback=None):
    """
    Convenience function to notify guardian asynchronously
    
    Args:
        phone_number (str): Guardian's phone number
        child_name (str): Child's name
        found_location (str, optional): Where the child was found
        custom_message (str, optional): Custom message to add
        callback (function, optional): Function to call after completion
    """
    notifier = GuardianNotifier()
    return notifier.notify_guardian_async(phone_number, child_name, found_location, 
                                        custom_message, callback)

def notify_multiple_guardians(phone_numbers, child_name, found_location=None, custom_message=None):
    """
    Notify multiple guardians for the same child
    
    Args:
        phone_numbers (list): List of guardian phone numbers
        child_name (str): Child's name
        found_location (str, optional): Where the child was found
        custom_message (str, optional): Custom message to add
        
    Returns:
        dict: Dictionary mapping phone numbers to (success_bool, method_used)
    """
    notifier = GuardianNotifier()
    results = {}
    
    for phone_number in phone_numbers:
        result, method = notifier.notify_guardian(phone_number, child_name, 
                                                 found_location, custom_message)
        results[phone_number] = (result, method)
    
    return results

def notify_multiple_guardians_async(phone_numbers, child_name, found_location=None, 
                                   custom_message=None, callback=None):
    """
    Notify multiple guardians asynchronously
    
    Args:
        phone_numbers (list): List of guardian phone numbers
        child_name (str): Child's name
        found_location (str, optional): Where the child was found
        custom_message (str, optional): Custom message to add
        callback (function, optional): Function to call after all notifications are sent
            Callback signature: callback(results_dict)
    """
    def _notify_thread():
        results = {}
        for phone_number in phone_numbers:
            notifier = GuardianNotifier()
            result, method = notifier.notify_guardian(
                phone_number, child_name, found_location, custom_message
            )
            results[phone_number] = (result, method)
        
        if callback:
            callback(results)
    
    # Start notification in a separate thread to avoid blocking GUI
    thread = threading.Thread(target=_notify_thread)
    thread.daemon = True
    thread.start()
    
    return thread