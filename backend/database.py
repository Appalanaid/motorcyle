"""
Database connection and utilities for SQL Server integration.
Handles connection pooling and query execution.
"""

import pyodbc
from typing import Optional, List, Dict, Any
from config import get_settings

settings = get_settings()


class DatabaseConnection:
    """
    Manages SQL Server database connections and operations.
    Uses ODBC for connection to SQL Server.
    """

    def __init__(self):
        """Initialize database connection string."""
        if settings.use_windows_auth:
            # Use Windows authentication
            self.connection_string = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={settings.db_server};"
                f"DATABASE={settings.db_database};"
                f"Trusted_Connection=yes"
            )
        else:
            # Use SQL Server authentication
            self.connection_string = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={settings.db_server};"
                f"DATABASE={settings.db_database};"
                f"UID={settings.db_user};"
                f"PWD={settings.db_password}"
            )
        self.connection: Optional[pyodbc.Connection] = None

    def connect(self) -> pyodbc.Connection:
        """
        Establish connection to SQL Server database.
        
        Returns:
            pyodbc.Connection: Active database connection
        """
        try:
            self.connection = pyodbc.connect(self.connection_string)
            return self.connection
        except pyodbc.Error as e:
            print(f"Database connection error: {e}")
            raise

    def disconnect(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()

    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        Execute SELECT query and return results as list of dictionaries.
        
        Args:
            query: SQL SELECT query
            params: Query parameters for parameterized queries
            
        Returns:
            List of dictionaries with query results
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            
            # Get column names
            columns = [description[0] for description in cursor.description]
            
            # Fetch all rows and convert to dictionaries
            rows = []
            for row in cursor.fetchall():
                rows.append(dict(zip(columns, row)))
            
            cursor.close()
            return rows
        except pyodbc.Error as e:
            print(f"Query execution error: {e}")
            raise

    def execute_update(self, query: str, params: tuple = ()) -> int:
        """
        Execute INSERT, UPDATE, or DELETE query.
        
        Args:
            query: SQL modification query
            params: Query parameters
            
        Returns:
            Number of affected rows
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            rows_affected = cursor.rowcount
            self.connection.commit()
            cursor.close()
            return rows_affected
        except pyodbc.Error as e:
            self.connection.rollback()
            print(f"Update execution error: {e}")
            raise


# Global database instance
_db_instance: Optional[DatabaseConnection] = None


def get_db() -> DatabaseConnection:
    """Get or create database connection instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseConnection()
        _db_instance.connect()
    return _db_instance
