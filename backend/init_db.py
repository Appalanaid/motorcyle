"""
Database initialization and SQL schema creation.
Run this script to initialize the Bike_DB database with required tables.
"""

import pyodbc
from dotenv import load_dotenv
from config import get_settings

# Load .env file
load_dotenv()

settings = get_settings()


def create_motorcycles_table():
    """
    Create the Motorcycles table in Bike_DB with industry best practices.
    Includes normalization, constraints, and comprehensive specifications.
    
    Columns:
    - bike_id: Primary key, auto-increment
    - name: Model name (indexed for search)
    - brand: Manufacturer brand (indexed)
    - seat_height_cm: Seat height for ergonomic matching
    - weight_kg: Dry weight for compatibility scoring
    - engine_cc: Engine displacement
    - riding_style: Category (naked, sport, cruiser, adventure, touring)
    - year: Model year
    - price_usd: MSRP price
    - comfort_rating, performance_rating, reliability_rating: 1-10 scale
    - fuel_capacity_liters: Tank capacity
    - max_speed_kmh: Top speed specification
    - torque_nm: Engine torque
    - transmission: Manual/Automatic/CVT
    - abs_available: Anti-lock braking system
    - traction_control: Traction control available
    - active: Soft delete flag
    - created_date, updated_date: Audit timestamps
    """
    create_table_sql = """
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Motorcycles' and xtype='U')
    CREATE TABLE Motorcycles (
        bike_id INT PRIMARY KEY IDENTITY(1,1),
        name NVARCHAR(100) NOT NULL,
        brand NVARCHAR(100) NOT NULL,
        seat_height_cm FLOAT NOT NULL CHECK (seat_height_cm > 0),
        weight_kg FLOAT NOT NULL CHECK (weight_kg > 0),
        engine_cc INT NOT NULL CHECK (engine_cc > 0),
        riding_style NVARCHAR(50) NOT NULL,
        year INT CHECK (year >= 1900 AND year <= 2100),
        price_usd DECIMAL(10, 2) CHECK (price_usd >= 0),
        comfort_rating FLOAT CHECK (comfort_rating >= 0 AND comfort_rating <= 10),
        performance_rating FLOAT CHECK (performance_rating >= 0 AND performance_rating <= 10),
        reliability_rating FLOAT CHECK (reliability_rating >= 0 AND reliability_rating <= 10),
        fuel_capacity_liters FLOAT CHECK (fuel_capacity_liters > 0),
        max_speed_kmh INT CHECK (max_speed_kmh > 0),
        torque_nm FLOAT CHECK (torque_nm > 0),
        transmission NVARCHAR(50),
        abs_available BIT DEFAULT 0,
        traction_control BIT DEFAULT 0,
        active BIT DEFAULT 1,
        created_date DATETIME DEFAULT GETDATE(),
        updated_date DATETIME DEFAULT GETDATE()
    );
    
    -- Create indexes for frequently queried columns
    IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name='IX_Motorcycles_Brand')
    CREATE INDEX IX_Motorcycles_Brand ON Motorcycles(brand);
    
    IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name='IX_Motorcycles_RidingStyle')
    CREATE INDEX IX_Motorcycles_RidingStyle ON Motorcycles(riding_style);
    
    IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name='IX_Motorcycles_SeatHeight')
    CREATE INDEX IX_Motorcycles_SeatHeight ON Motorcycles(seat_height_cm);
    
    IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name='IX_Motorcycles_Active')
    CREATE INDEX IX_Motorcycles_Active ON Motorcycles(active);
    """
    return create_table_sql


def create_recommendations_table():
    """
    Create Recommendations table to store user recommendations with full audit trail.
    Follows normalization principles with proper foreign keys and constraints.
    
    Columns:
    - recommendation_id: Primary key
    - user_height_cm: User height for matching
    - user_weight_kg: User weight for compatibility
    - user_inseam_cm: Calculated inseam from image analysis
    - riding_preference: User's preferred riding style
    - recommended_bike_id: Foreign key to Motorcycles
    - overall_score: Final recommendation score (0-100)
    - seat_height_score, weight_score, preference_score: Component scores
    - explanation: Detailed recommendation reason
    - uploaded_image_url: Path to user's uploaded photo
    - generated_image_url: Path to AI-generated image
    - user_feedback: Optional user satisfaction feedback
    - created_date: Timestamp for analytics
    """
    create_table_sql = """
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Recommendations' and xtype='U')
    CREATE TABLE Recommendations (
        recommendation_id INT PRIMARY KEY IDENTITY(1,1),
        user_height_cm FLOAT NOT NULL CHECK (user_height_cm > 0),
        user_weight_kg FLOAT NOT NULL CHECK (user_weight_kg > 0),
        user_inseam_cm FLOAT,
        riding_preference NVARCHAR(50) NOT NULL,
        recommended_bike_id INT NOT NULL,
        overall_score FLOAT CHECK (overall_score >= 0 AND overall_score <= 100),
        seat_height_score FLOAT CHECK (seat_height_score >= 0 AND seat_height_score <= 100),
        weight_score FLOAT CHECK (weight_score >= 0 AND weight_score <= 100),
        preference_score FLOAT CHECK (preference_score >= 0 AND preference_score <= 100),
        explanation NVARCHAR(MAX),
        uploaded_image_url NVARCHAR(MAX),
        generated_image_url NVARCHAR(MAX),
        user_feedback NVARCHAR(500),
        created_date DATETIME DEFAULT GETDATE(),
        FOREIGN KEY (recommended_bike_id) REFERENCES Motorcycles(bike_id)
    );
    
    -- Create indexes for query performance
    IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name='IX_Recommendations_BikeId')
    CREATE INDEX IX_Recommendations_BikeId ON Recommendations(recommended_bike_id);
    
    IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name='IX_Recommendations_CreatedDate')
    CREATE INDEX IX_Recommendations_CreatedDate ON Recommendations(created_date);
    
    IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name='IX_Recommendations_OverallScore')
    CREATE INDEX IX_Recommendations_OverallScore ON Recommendations(overall_score);
    """
    return create_table_sql


def insert_sample_motorcycles():
    """
    Insert comprehensive sample motorcycle data based on industry best practices.
    Data sourced from manufacturer specifications and industry reviews.
    Includes real-world metrics for accurate recommendations.
    """
    insert_sql = """
    IF NOT EXISTS (SELECT 1 FROM Motorcycles WHERE bike_id = 1)
    BEGIN
        INSERT INTO Motorcycles 
        (name, brand, seat_height_cm, weight_kg, engine_cc, riding_style, year, price_usd, 
         comfort_rating, performance_rating, reliability_rating, fuel_capacity_liters, 
         max_speed_kmh, torque_nm, transmission, abs_available, traction_control)
        VALUES
        -- Entry-level Commuter/Learner Bikes
        ('CB300F', 'Honda', 73, 130, 300, 'naked', 2023, 4150, 8.0, 7.5, 9.5, 15.0, 180, 25.7, 'Manual', 1, 0),
        ('Rebel 300', 'Honda', 68, 165, 300, 'cruiser', 2023, 4400, 8.5, 6.5, 9.5, 11.0, 160, 26.5, 'Manual', 0, 0),
        ('CBR500F', 'Honda', 78, 189, 471, 'sport', 2023, 6299, 7.5, 8.0, 9.4, 15.7, 195, 43.0, 'Manual', 1, 1),
        
        -- Mid-range Naked/Street Bikes
        ('MT-07', 'Yamaha', 82, 184, 689, 'naked', 2023, 7299, 8.2, 8.7, 8.9, 15.0, 220, 68.0, 'Manual', 1, 1),
        ('CB650R', 'Honda', 81, 208, 649, 'naked', 2023, 7449, 8.3, 8.5, 9.3, 15.0, 210, 63.0, 'Manual', 1, 1),
        ('GSX-S750', 'Suzuki', 80, 203, 749, 'naked', 2023, 7399, 8.1, 8.6, 8.8, 15.0, 225, 72.0, 'Manual', 1, 1),
        
        -- Adventure/Touring Bikes
        ('V-Strom 650', 'Suzuki', 82, 216, 645, 'adventure', 2023, 7699, 8.3, 7.9, 8.9, 20.0, 200, 62.0, 'Manual', 1, 1),
        ('CB500X', 'Honda', 81, 189, 471, 'adventure', 2023, 6649, 8.4, 7.8, 9.3, 17.3, 190, 43.0, 'Manual', 1, 1),
        
        -- Cruiser Bikes (Large & Comfortable)
        ('Royal Enfield Classic 350', 'Royal Enfield', 78, 202, 350, 'cruiser', 2023, 4345, 8.4, 6.8, 8.2, 13.0, 150, 28.0, 'Manual', 0, 0),
        ('Rebel 500', 'Honda', 72, 190, 471, 'cruiser', 2023, 5999, 8.6, 7.2, 9.4, 11.0, 180, 43.0, 'Manual', 0, 0),
        
        -- Sport/Performance Bikes
        ('Ninja 400', 'Kawasaki', 78, 168, 399, 'sport', 2023, 4699, 7.8, 7.9, 8.7, 15.0, 180, 37.0, 'Manual', 1, 0),
        ('YZF-R7', 'Yamaha', 82, 184, 689, 'sport', 2023, 7549, 7.6, 8.9, 8.9, 15.0, 230, 68.0, 'Manual', 1, 1),
        ('GSX-R750', 'Suzuki', 82, 207, 749, 'sport', 2023, 7999, 7.4, 9.1, 8.7, 16.0, 240, 75.0, 'Manual', 1, 1),
        
        -- Tall Rider/Adventure Touring (87+ cm seat)
        ('Africa Twin', 'Honda', 87, 245, 1084, 'adventure', 2023, 15199, 8.6, 8.5, 9.2, 24.0, 220, 101.0, 'Manual', 1, 1),
        ('Versys 1000', 'Kawasaki', 84, 238, 1043, 'adventure', 2023, 12999, 8.4, 8.3, 8.9, 19.0, 230, 102.0, 'Manual', 1, 1),
        ('Tracer 9 GT', 'Yamaha', 82, 203, 889, 'sport touring', 2023, 10399, 8.5, 8.4, 8.9, 18.0, 225, 89.0, 'Manual', 1, 1),
        
        -- Premium/Luxury Options
        ('Pan America 1250', 'Harley-Davidson', 85, 268, 1252, 'adventure', 2023, 14995, 8.7, 8.2, 8.5, 22.0, 210, 126.0, 'Manual', 1, 1),
        ('Gold Wing', 'Honda', 76, 383, 1833, 'touring', 2023, 23550, 9.0, 7.5, 9.4, 21.0, 200, 170.0, 'Automatic', 1, 1),
        
        -- Small/Beginner Friendly
        ('CB125R', 'Honda', 72, 130, 125, 'naked', 2023, 2149, 7.9, 6.0, 9.6, 8.0, 130, 11.0, 'Manual', 0, 0),
        ('YZF-R125', 'Yamaha', 78, 142, 125, 'sport', 2023, 3199, 7.5, 7.0, 8.9, 7.7, 140, 11.0, 'Manual', 0, 0)
    END
    """
    return insert_sql


def initialize_database():
    """
    Initialize Bike_DB with required tables and sample data.
    """
    try:
        # Connect to SQL Server
        if settings.use_windows_auth:
            # Use Windows authentication for development
            connection_string = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={settings.db_server};"
                f"DATABASE={settings.db_database};"
                f"Trusted_Connection=yes"
            )
            print("Using Windows Authentication")
        else:
            # Use SQL Server authentication with credentials
            connection_string = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={settings.db_server};"
                f"DATABASE={settings.db_database};"
                f"UID={settings.db_user};"
                f"PWD={settings.db_password}"
            )
            print("Using SQL Server Authentication")
        
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        print("Creating Motorcycles table...")
        cursor.execute(create_motorcycles_table())
        conn.commit()

        print("Creating Recommendations table...")
        cursor.execute(create_recommendations_table())
        conn.commit()

        print("Inserting sample motorcycles...")
        cursor.execute(insert_sample_motorcycles())
        conn.commit()

        print("Database initialization complete!")
        
        cursor.close()
        conn.close()

    except pyodbc.Error as e:
        print(f"Database error: {e}")
        raise
    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    print("Initializing Bike_DB database...")
    initialize_database()
