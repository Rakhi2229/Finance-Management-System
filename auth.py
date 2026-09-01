"""
=============================================================================
FINTRACK - PERSONAL FINANCE MANAGEMENT SYSTEM
Module: auth.py
Description: User authentication logic, secure password hashing using bcrypt,
             input validation, and Streamlit session-state management.
=============================================================================
"""

import re  # Import regex module for validating email syntax
import bcrypt  # Import bcrypt for cryptographic password hashing and verification
import streamlit as st  # Import Streamlit for session-state authentication handling
from database import SessionLocal, User  # Import database session and User ORM model


# ---------------------------------------------------------------------------
# 1. PASSWORD CRYPTOGRAPHY FUNCTIONS
# ---------------------------------------------------------------------------

def hash_password(password: str) -> str:
    """
    Hash a plaintext password using bcrypt with a securely generated salt.

    Parameters:
        password (str): The plaintext password string entered by the user.

    Returns:
        str: The UTF-8 decoded bcrypt password hash string ready for database storage.
    """
    # Convert the string password into UTF-8 bytes because bcrypt operates on raw bytes
    password_bytes = password.encode("utf-8")

    # Generate a unique cryptographic salt (work factor default: 12 rounds)
    salt = bcrypt.gensalt()

    # Hash the password bytes with the generated salt
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)

    # Decode bytes to a UTF-8 string for clean storage in SQLite database column
    return hashed_bytes.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify whether a plaintext password matches the stored bcrypt hash.

    Parameters:
        plain_password (str): The candidate password entered during login.
        hashed_password (str): The bcrypt hash retrieved from the database.

    Returns:
        bool: True if the password matches the hash, False otherwise.
    """
    try:
        # Encode both plaintext password and stored hash into UTF-8 bytes for comparison
        plain_bytes = plain_password.encode("utf-8")
        hash_bytes = hashed_password.encode("utf-8")

        # Use bcrypt's constant-time comparison to prevent timing attacks
        return bcrypt.checkpw(plain_bytes, hash_bytes)
    except Exception as e:
        # If hash format is invalid or corrupted, fail safely
        print(f"[Auth Error] Password verification failed: {e}")
        return False


# ---------------------------------------------------------------------------
# 2. INPUT VALIDATION HELPERS
# ---------------------------------------------------------------------------

def validate_email_format(email: str) -> bool:
    """
    Validate that an email string conforms to standard email format (name@domain.com).

    Parameters:
        email (str): The candidate email address.

    Returns:
        bool: True if valid email format, False otherwise.
    """
    # Regex pattern: alphanumeric + certain special characters @ domain . top-level-domain
    email_regex = r"^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$"

    # Match the email against the regex pattern
    return bool(re.match(email_regex, email.strip()))


# ---------------------------------------------------------------------------
# 3. USER REGISTRATION & LOGIN BUSINESS LOGIC
# ---------------------------------------------------------------------------

def register_user(full_name: str, email: str, password: str, confirm_password: str) -> tuple[bool, str]:
    """
    Register a new user account with strict field validation and password hashing.

    Parameters:
        full_name (str): The full name of the user.
        email (str): The user's email address (must be unique).
        password (str): The desired password.
        confirm_password (str): Password confirmation string to verify accuracy.

    Returns:
        tuple[bool, str]: (Success boolean, Descriptive message)
    """
    # Sanitize string inputs by stripping outer whitespaces
    full_name = full_name.strip()
    email = email.strip().lower()

    # Step 1: Validate that required fields are not empty
    if not full_name or not email or not password or not confirm_password:
        return False, "All registration fields are required. Please fill in all fields."

    # Step 2: Validate email address format
    if not validate_email_format(email):
        return False, "Invalid email format. Please enter a valid email address (e.g. user@example.com)."

    # Step 3: Validate minimum password length for security
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."

    # Step 4: Validate password confirmation match
    if password != confirm_password:
        return False, "Passwords do not match. Please ensure both passwords are identical."

    # Step 5: Check database for duplicate email registrations
    session = SessionLocal()
    try:
        # Query for any existing user with the same email
        existing_user = session.query(User).filter(User.email == email).first()
        if existing_user:
            return False, "An account with this email address already exists. Please log in."

        # Step 6: Hash password securely with bcrypt
        hashed_pw = hash_password(password)

        # Step 7: Create a new User ORM record
        new_user = User(
            full_name=full_name,
            email=email,
            password_hash=hashed_pw
        )

        # Add to database session and commit transaction
        session.add(new_user)
        session.commit()

        return True, "Account registered successfully! You can now log in."

    except Exception as e:
        # Roll back transaction if an unexpected database error occurs
        session.rollback()
        return False, f"Registration failed due to a database error: {str(e)}"
    finally:
        # Always close the session to avoid connection leaks
        session.close()


def login_user(email: str, password: str) -> tuple[bool, str, dict | None]:
    """
    Authenticate a user by verifying email existence and comparing bcrypt password hashes.

    Parameters:
        email (str): The user's registered email address.
        password (str): The plaintext password provided during login.

    Returns:
        tuple[bool, str, dict | None]:
            - bool: True if authentication succeeded, False otherwise.
            - str: Descriptive status message.
            - dict | None: User details dict (user_id, full_name, email) if successful, else None.
    """
    # Sanitize email input
    email = email.strip().lower()

    # Step 1: Validate input completeness
    if not email or not password:
        return False, "Please enter both your email address and password.", None

    # Step 2: Query database for the user record
    session = SessionLocal()
    try:
        # Retrieve user with matching email
        user = session.query(User).filter(User.email == email).first()

        # If user not found, return a generic message to prevent account enumeration
        if not user:
            return False, "Invalid email or password. Please try again.", None

        # Step 3: Verify plaintext password against stored bcrypt hash
        if not verify_password(password, user.password_hash):
            return False, "Invalid email or password. Please try again.", None

        # Step 4: Authentication succeeded — bundle user info into a clean dictionary
        user_data = {
            "user_id": user.user_id,
            "full_name": user.full_name,
            "email": user.email
        }
        return True, "Login successful!", user_data

    except Exception as e:
        return False, f"Login error: {str(e)}", None
    finally:
        session.close()


# ---------------------------------------------------------------------------
# 4. STREAMLIT SESSION STATE MANAGEMENT
# ---------------------------------------------------------------------------

def init_session_state():
    """
    Initialize essential authentication keys in Streamlit's session_state.

    Ensures that session keys are defined before any component attempts to read them,
    preventing KeyError exceptions during page rendering.
    """
    # 'logged_in' boolean tracks user authentication status
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    # 'user_id' holds the primary key of the authenticated user (used for all queries)
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = None

    # 'user_name' stores the user's full name for UI greetings
    if "user_name" not in st.session_state:
        st.session_state["user_name"] = ""

    # 'user_email' stores the logged-in email
    if "user_email" not in st.session_state:
        st.session_state["user_email"] = ""


def set_user_session(user_id: int, full_name: str, email: str):
    """
    Store authenticated user credentials in Streamlit session state upon successful login.

    Parameters:
        user_id (int): Primary key ID of the logged-in user.
        full_name (str): Full name of the user.
        email (str): Registered email address of the user.
    """
    st.session_state["logged_in"] = True
    st.session_state["user_id"] = user_id
    st.session_state["user_name"] = full_name
    st.session_state["user_email"] = email


def logout_user():
    """
    Log out the currently active user by resetting authentication keys in session state
    and triggering a Streamlit rerun to immediately present the login screen.
    """
    st.session_state["logged_in"] = False
    st.session_state["user_id"] = None
    st.session_state["user_name"] = ""
    st.session_state["user_email"] = ""

    # Force a rerun so Streamlit immediately re-renders the unauthenticated view
    st.rerun()
