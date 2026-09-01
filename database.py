"""
=============================================================================
FINTRACK - PERSONAL FINANCE MANAGEMENT SYSTEM
Module: database.py
Description: Database configuration, SQLAlchemy ORM models, relationships,
             table creation, and session management.
=============================================================================
"""

import os  # Import os module for managing directory paths and file operations
from datetime import datetime  # Import datetime to timestamp record creations
from sqlalchemy import (  # Import SQLAlchemy core components for schema definition
    create_engine,
    Column,
    Integer,
    String,
    Float,
    Date,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import (  # Import ORM tools for declarative base, sessions, and relationships
    declarative_base,
    sessionmaker,
    relationship
)

# ---------------------------------------------------------------------------
# 1. DATABASE PATH & DIRECTORY CONFIGURATION
# ---------------------------------------------------------------------------

# Determine the absolute directory where this database.py file resides
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define the data folder path inside the project root directory
DATA_DIR = os.path.join(BASE_DIR, "data")

# Create the data directory automatically if it does not already exist
os.makedirs(DATA_DIR, exist_ok=True)

# Define the absolute path to the SQLite database file
DB_PATH = os.path.join(DATA_DIR, "finance.db")

# Create the SQLite connection string URL (sqlite:///path/to/db)
DATABASE_URL = f"sqlite:///{DB_PATH}"

# ---------------------------------------------------------------------------
# 2. SQLALCHEMY ENGINE & SESSION FACTORY
# ---------------------------------------------------------------------------

# Create the SQLAlchemy Engine
# 'check_same_thread=False' allows SQLite to be used safely across Streamlit's multi-threaded requests
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False  # Set to True if SQL query logging in terminal is desired
)

# Create a sessionmaker factory bound to the engine for creating database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create the Declarative Base class from which all ORM models will inherit
Base = declarative_base()


# ---------------------------------------------------------------------------
# 3. DATABASE MODELS (SCHEMA DEFINITION)
# ---------------------------------------------------------------------------

class User(Base):
    """
    User ORM Model

    Represents registered users in the FinTrack system.
    Every financial transaction (income, expense, budget) is strictly associated
    with a single User record via foreign keys to guarantee data isolation.
    """
    __tablename__ = "users"  # Name of the database table

    # Primary key: Unique identifier for each user
    user_id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    # User's full name for dashboard greetings and profile display
    full_name = Column(String(100), nullable=False)

    # Unique email address used as the login credential
    email = Column(String(120), unique=True, nullable=False, index=True)

    # Securely hashed password generated using bcrypt (never plaintext)
    password_hash = Column(String(255), nullable=False)

    # Timestamp when the user account was registered
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships: Cascade deletes all child records when a user is deleted
    incomes = relationship(
        "Income",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    expenses = relationship(
        "Expense",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    budgets = relationship(
        "Budget",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        """String representation of the User model instance."""
        return f"<User(user_id={self.user_id}, email='{self.email}', name='{self.full_name}')>"


class Income(Base):
    """
    Income ORM Model

    Represents income earnings recorded by users (e.g., Salary, Freelance, Investments).
    """
    __tablename__ = "incomes"  # Name of the database table

    # Primary key: Unique identifier for each income record
    income_id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    # Foreign key referencing the user who owns this income record
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)

    # Monetary amount earned (must be positive)
    amount = Column(Float, nullable=False)

    # Source category of income (e.g., Salary, Freelance, Business, Investment, Interest, Other)
    source = Column(String(50), nullable=False)

    # Optional descriptive note about the income transaction
    description = Column(String(255), nullable=True)

    # Date when the income was received (used for filtering and monthly trends)
    income_date = Column(Date, nullable=False, index=True)

    # Timestamp when the record was inserted into the database
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Bidirectional relationship back to the User model
    user = relationship("User", back_populates="incomes")

    def __repr__(self):
        """String representation of the Income model instance."""
        return f"<Income(income_id={self.income_id}, user_id={self.user_id}, amount={self.amount}, source='{self.source}')>"


class Expense(Base):
    """
    Expense ORM Model

    Represents expenditures recorded by users (e.g., Food, Rent, Transportation).
    """
    __tablename__ = "expenses"  # Name of the database table

    # Primary key: Unique identifier for each expense record
    expense_id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    # Foreign key referencing the user who owns this expense record
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)

    # Monetary amount spent (must be positive)
    amount = Column(Float, nullable=False)

    # Expense category (e.g., Food, Rent, Transportation, Shopping, Bills, etc.)
    category = Column(String(50), nullable=False, index=True)

    # Optional descriptive note about the purchase or transaction
    description = Column(String(255), nullable=True)

    # Payment method used (e.g., Cash, UPI, Debit Card, Credit Card, Bank Transfer)
    payment_method = Column(String(50), nullable=False)

    # Date when the expense occurred (used for monthly aggregations & budget tracking)
    expense_date = Column(Date, nullable=False, index=True)

    # Timestamp when the record was created
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Bidirectional relationship back to the User model
    user = relationship("User", back_populates="expenses")

    def __repr__(self):
        """String representation of the Expense model instance."""
        return f"<Expense(expense_id={self.expense_id}, user_id={self.user_id}, amount={self.amount}, category='{self.category}')>"


class Budget(Base):
    """
    Budget ORM Model

    Represents monthly spending limits set by users for specific expense categories.
    """
    __tablename__ = "budgets"  # Name of the database table

    # Primary key: Unique identifier for each budget record
    budget_id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    # Foreign key referencing the user who set this budget
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)

    # Expense category being budgeted (e.g., Food, Shopping, Entertainment)
    category = Column(String(50), nullable=False)

    # Maximum allocated spending amount for the given category in that month
    monthly_limit = Column(Float, nullable=False)

    # Month of the budget allocation (1 to 12)
    month = Column(Integer, nullable=False)

    # Year of the budget allocation (e.g., 2025, 2026)
    year = Column(Integer, nullable=False)

    # Timestamp when the budget target was created
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Bidirectional relationship back to the User model
    user = relationship("User", back_populates="budgets")

    def __repr__(self):
        """String representation of the Budget model instance."""
        return f"<Budget(budget_id={self.budget_id}, user_id={self.user_id}, category='{self.category}', limit={self.monthly_limit}, month={self.month}/{self.year})>"


# ---------------------------------------------------------------------------
# 4. DATABASE INITIALIZATION & SESSION HELPER FUNCTIONS
# ---------------------------------------------------------------------------

def init_db():
    """
    Initialize the SQLite database schema.

    Creates all database tables defined in the Base metadata if they do not
    already exist in the data/finance.db file.

    Returns:
        bool: True if initialization was successful, False otherwise.
    """
    try:
        # Create all registered tables (users, incomes, expenses, budgets)
        Base.metadata.create_all(bind=engine)
        return True
    except Exception as e:
        # Print error details to console if table creation fails
        print(f"[Database Error] Table creation failed: {e}")
        return False


def get_db():
    """
    Context manager / generator for acquiring a database session.

    Yields a SQLAlchemy SessionLocal instance and ensures proper cleanup
    (closing the session) even if an exception occurs during the transaction.

    Yields:
        Session: Active SQLAlchemy database session.
    """
    session = SessionLocal()  # Instantiate a new session from our factory
    try:
        yield session  # Provide session to calling code block
    finally:
        session.close()  # Always close session to release connection back to pool
