"""
Classifier module for detecting and classifying prompt injections.

This module provides functionality to:
- Detect whether a given input is a benign or malicious prompt injection.
- Classify the type of malicious prompt injection if applicable.
- Log detected malicious inputs for auditing purposes.
"""

import joblib
import os
import json
from pathlib import Path

# Define paths for the models and supporting files
PACKAGE_DIR = os.path.dirname(__file__)
BINARY_CLASSIFIER_PATH = os.path.join(PACKAGE_DIR, "models/optimised_binary_classifier.pkl")
MULTI_CLASS_CLASSIFIER_PATH = os.path.join(PACKAGE_DIR, "models/optimised_multi_class_classifier.pkl")
TFIDF_BINARY_PATH = os.path.join(PACKAGE_DIR, "models/optimised_tfidf_vectorizer_binary.pkl")
TFIDF_MULTI_PATH = os.path.join(PACKAGE_DIR, "models/optimised_tfidf_vectorizer_multi.pkl")
LABEL_ENCODER_PATH = os.path.join(PACKAGE_DIR, "models/optimised_label_encoder_multi.pkl")

# Load models and transformers
binary_classifier = joblib.load(BINARY_CLASSIFIER_PATH)
multi_class_classifier = joblib.load(MULTI_CLASS_CLASSIFIER_PATH)
tfidf_vectorizer_binary = joblib.load(TFIDF_BINARY_PATH)
tfidf_vectorizer_multi = joblib.load(TFIDF_MULTI_PATH)
label_encoder_multi = joblib.load(LABEL_ENCODER_PATH)

# Initialize the log file path as a global variable
log_file_path = None

SCRIPT_DIR = Path(__file__).parent
CONFIG_PATH = SCRIPT_DIR / "prompt_classifier_config.json"

def load_config():
    """
    Loads the configuration file that contains the user's preferred save location. If the file does not exist, an empty config is returned.

    Returns:
        dict: Configuration dictionary.
    """
    config_path = Path.cwd() / "prompt_classifier_config.json"
    if config_path.exists():
        try:
            with open(config_path, "r") as config_file:
                return json.load(config_file)
        except json.JSONDecodeError:
            print("Config file is corrupted. A new one will be created.")
            return {}
    return {}

def save_config(config):
    """
    Saves the configuration to a file in the current working directory.

    Args:
        config (dict): Configuration data to save.
    """
    config_path = Path.cwd() / "prompt_classifier_config.json"
    with open(config_path, "w") as config_file:
        json.dump(config, config_file, indent=4)

def test_write_access(folder_path):
    """
    Tests write access to a specified folder by attempting to create and delete a test file.

    Args:
        folder_path (str): The path to the folder to test.

    Returns:
        bool: True if the folder is writable, False otherwise.
    """
    try:
        if not os.path.isdir(folder_path):
            print(f"The path {folder_path} is not an existing directory.")
            return False
        test_file = Path(folder_path) / "test_write.txt"
        test_file.write_text("Write test successful.")
        test_file.unlink()  # Remove the test file
        print(f"Write access confirmed for: {folder_path}")
        return True
    except PermissionError as e:
        print(f"Permission denied for folder: {folder_path}. Error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error for folder: {folder_path}. Error: {e}")
        return False

def get_log_file_path():
    """
    Prompts the user to specify a valid and writable directory for the log file.

    Returns:
        pathlib.Path: The path to the log file.
    """
    global log_file_path

    # Load existing configuration
    config = load_config()

    # Check if log file path is saved in config
    if "log_file_path" in config:
        log_file_path = Path(config["log_file_path"])
        if log_file_path.exists() or test_write_access(log_file_path.parent):
            #print(f"Using saved log file location: {log_file_path}")
            return log_file_path
        
    else:
        print("Saved config file is invalid, if it is your first time running the classify_input function ignore this message")

    desktop_path = Path.home() / "Desktop"
    print(f"Select a location for your log file. Default: {desktop_path / 'prompt_injection_log.json'}")

    while True:
        log_file_input = input("Enter the log file path: ").strip()
        log_file_path = Path(log_file_input) if log_file_input else desktop_path / "prompt_injection_log.json"

        if not log_file_input:
            # Default case: desktop
            log_file_path = desktop_path / "prompt_injection_log.json"
            break

        if not log_file_path.is_absolute():
            print("Please provide an absolute path. Relative paths are not allowed.")
            continue

        if not os.path.isdir(log_file_input):
            print(f"The directory {log_file_input} does not exist. Please enter a valid directory.")
            continue
        
        if log_file_path.is_dir():
            log_file_path = log_file_path / "prompt_injection_log.json"
            break

        try:
            log_file_path.parent.mkdir(parents=True, exist_ok=True)
            if test_write_access(log_file_path.parent):
                #save the details of the user's preferred save location into the config file
                config["log_file_path"] = str(log_file_path)
                save_config(config)
                print(f"Log file initialized at: {log_file_path}")
                break
            if not log_file_path.exists():
                log_file_path.write_text("[]")  # Initialize the log file with an empty JSON array
                continue
        except Exception as e:
            print(f"An error occurred while creating the log file: {e}")   
   
    try:
        log_file_path.parent.mkdir(parents=True, exist_ok=True)
        if test_write_access(log_file_path.parent):
            #save the details of the user's preferred save location into the config file
            config["log_file_path"] = str(log_file_path)
            save_config(config)
        if not log_file_path.exists():
            log_file_path.write_text("[]")  # Initialize the log file with an empty JSON array
        print(f"Log file initialized at: {log_file_path}")
    except Exception as e:
        print(f"An error occurred while creating the log file: {e}")

    return log_file_path

def log_malicious_input(user_input, detection_result):
    """
    Logs malicious prompt injections to a specified log file.

    Args:
        user_input (str): The input text flagged as malicious.
        detection_result (dict): Detection result containing 'is_prompt_injection' and 'class'.
    """
    log_file_path = get_log_file_path()

    if not os.path.exists(log_file_path):
        with open(log_file_path, "w") as log_file:
            json.dump([], log_file, indent=4)

    log_entry = {
        "input": user_input,
        "detection": detection_result["is_prompt_injection"],
        "class": detection_result["class"]
    }

    with open(log_file_path, "r+") as log_file:
        logs = json.load(log_file)
        logs.append(log_entry)
        log_file.seek(0)
        json.dump(logs, log_file, indent=4)

def classify_input(user_input: str) -> dict:
    """
    Classifies the user input as benign or a prompt injection and determines its class.

    Args:
        user_input (str): The input text to classify.

    Returns:
        dict: Classification result with:
            - is_prompt_injection (str): Whether the input is benign or a prompt injection.
            - class (str): The class of the input.
    """
    input_tfidf_binary = tfidf_vectorizer_binary.transform([user_input])
    is_prompt_injection = binary_classifier.predict(input_tfidf_binary)[0]

    if is_prompt_injection == 0:
        return {
            "is_prompt_injection": "Benign",
            "class": "benign"
        }
    else:
        input_tfidf_multi = tfidf_vectorizer_multi.transform([user_input])
        predicted_class_index = multi_class_classifier.predict(input_tfidf_multi)[0]
        predicted_class = label_encoder_multi.inverse_transform([predicted_class_index])[0]
        result = {
            "is_prompt_injection": "Legitimate Prompt Injection",
            "class": predicted_class
        }

        log_malicious_input(user_input, result)
        return result
