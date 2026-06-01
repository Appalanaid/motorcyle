"""
Motorcycle recommendation engine.
Uses rule-based logic to match user characteristics with suitable bikes.
"""

from typing import List, Tuple
from models import BodyAnalysis, Motorcycle, RidingPreference
from database import get_db


class RecommendationEngine:
    """
    Rule-based motorcycle recommendation system.
    Matches user physical characteristics with motorcycle specifications.
    """

    # Seat height tolerance (cm) - user comfortable if seat height within range
    SEAT_HEIGHT_TOLERANCE = 5

    # Weight comfort ratio - user weight should not exceed this ratio of bike weight
    MAX_WEIGHT_RATIO = 1.5

    def __init__(self):
        """Initialize recommendation engine with database connection."""
        self.db = get_db()
        self.riding_preference_weights = {
            "commute": {"naked": 0.8, "cruiser": 0.6, "sport": 0.4, "adventure": 0.7},
            "touring": {"cruiser": 0.9, "adventure": 0.95, "naked": 0.7, "sport": 0.3},
            "sport": {"sport": 0.95, "naked": 0.8, "cruiser": 0.3, "adventure": 0.5}
        }

    def get_all_motorcycles(self) -> List[Motorcycle]:
        """
        Fetch all motorcycles from database.
        
        Returns:
            List of Motorcycle objects
        """
        query = """
        SELECT 
            bike_id,
            name,
            brand,
            seat_height_cm,
            weight_kg,
            engine_cc,
            riding_style
        FROM Motorcycles
        WHERE active = 1
        ORDER BY seat_height_cm
        """
        try:
            rows = self.db.execute_query(query)
            motorcycles = []
            for row in rows:
                motorcycles.append(Motorcycle(**row))
            return motorcycles
        except Exception as e:
            print(f"Error fetching motorcycles: {e}")
            # Return sample data if database fails
            return self._get_sample_motorcycles()

    def _get_sample_motorcycles(self) -> List[Motorcycle]:
        """
        Sample motorcycle data for development/testing.
        Replace with database queries in production.
        
        Returns:
            List of sample Motorcycle objects
        """
        return [
            # Commuter bikes - low seat height, light weight
            Motorcycle(
                bike_id=1,
                name="CB300F",
                brand="Honda",
                seat_height_cm=73,
                weight_kg=130,
                engine_cc=300,
                riding_style="naked"
            ),
            Motorcycle(
                bike_id=2,
                name="Rebel 300",
                brand="Honda",
                seat_height_cm=68,
                weight_kg=165,
                engine_cc=300,
                riding_style="cruiser"
            ),
            # Mid-range bikes
            Motorcycle(
                bike_id=3,
                name="MT-07",
                brand="Yamaha",
                seat_height_cm=82,
                weight_kg=184,
                engine_cc=689,
                riding_style="naked"
            ),
            Motorcycle(
                bike_id=4,
                name="V-Strom 650",
                brand="Suzuki",
                seat_height_cm=82,
                weight_kg=216,
                engine_cc=645,
                riding_style="adventure"
            ),
            Motorcycle(
                bike_id=5,
                name="Royal Enfield Classic 350",
                brand="Royal Enfield",
                seat_height_cm=78,
                weight_kg=202,
                engine_cc=350,
                riding_style="cruiser"
            ),
            # Sport bikes - higher seat, more aggressive
            Motorcycle(
                bike_id=6,
                name="Ninja 400",
                brand="Kawasaki",
                seat_height_cm=78,
                weight_kg=168,
                engine_cc=399,
                riding_style="sport"
            ),
            Motorcycle(
                bike_id=7,
                name="YZF-R7",
                brand="Yamaha",
                seat_height_cm=82,
                weight_kg=184,
                engine_cc=689,
                riding_style="sport"
            ),
            # Tall rider friendly
            Motorcycle(
                bike_id=8,
                name="Africa Twin",
                brand="Honda",
                seat_height_cm=87,
                weight_kg=245,
                engine_cc=1084,
                riding_style="adventure"
            ),
        ]

    def calculate_seat_height_score(
        self,
        inseam_cm: float,
        seat_height_cm: float
    ) -> float:
        """
        Calculate suitability score based on seat height.
        Ideal range is inseam ± 5cm. Score decreases outside this range.
        
        Args:
            inseam_cm: User inseam length
            seat_height_cm: Motorcycle seat height
            
        Returns:
            Score 0-100
        """
        difference = abs(inseam_cm - seat_height_cm)
        
        if difference <= self.SEAT_HEIGHT_TOLERANCE:
            return 100.0
        elif difference <= 10:
            return 85.0 - (difference - self.SEAT_HEIGHT_TOLERANCE) * 3
        elif difference <= 15:
            return 70.0 - (difference - 10) * 2
        else:
            return max(30.0, 60.0 - difference)

    def calculate_weight_score(
        self,
        user_weight_kg: float,
        bike_weight_kg: float
    ) -> float:
        """
        Calculate suitability score based on weight compatibility.
        Heavier riders suit heavier bikes better (more stability).
        
        Args:
            user_weight_kg: User weight
            bike_weight_kg: Motorcycle weight
            
        Returns:
            Score 0-100
        """
        weight_ratio = user_weight_kg / bike_weight_kg
        
        # Ideal ratio: 0.5 to 1.5 (user weight is 50-150% of bike weight)
        if 0.5 <= weight_ratio <= 1.5:
            return 100.0 - (abs(weight_ratio - 1.0) * 50)  # Peak at 1.0
        elif weight_ratio < 0.5:
            # Rider too light - less stability
            return 60.0 + (weight_ratio * 80)
        else:
            # Rider too heavy - more effort needed
            return 100.0 - min(40.0, (weight_ratio - 1.5) * 40)

    def calculate_preference_score(
        self,
        riding_preference: RidingPreference,
        bike_style: str
    ) -> float:
        """
        Calculate suitability score based on riding preference match.
        
        Args:
            riding_preference: User riding preference (commute/touring/sport)
            bike_style: Motorcycle riding style category
            
        Returns:
            Score 0-100
        """
        weights = self.riding_preference_weights.get(
            riding_preference.value,
            {"naked": 0.5, "cruiser": 0.5, "sport": 0.5, "adventure": 0.5}
        )
        
        score = weights.get(bike_style, 50.0)
        return score * 100

    def calculate_overall_score(
        self,
        seat_score: float,
        weight_score: float,
        preference_score: float
    ) -> float:
        """
        Calculate overall suitability score with weighted average.
        
        Args:
            seat_score: Seat height compatibility (0-100)
            weight_score: Weight compatibility (0-100)
            preference_score: Riding preference match (0-100)
            
        Returns:
            Overall score (0-100)
        """
        # Weights: ergonomics (seat) is most important
        return (seat_score * 0.45 + weight_score * 0.25 + preference_score * 0.30)

    def recommend(
        self,
        height_cm: float,
        weight_kg: float,
        body_analysis: BodyAnalysis,
        riding_preference: RidingPreference,
        top_n: int = 1
    ) -> List[Tuple[Motorcycle, float, dict]]:
        """
        Generate motorcycle recommendations based on user characteristics.
        
        Args:
            height_cm: User height
            weight_kg: User weight
            body_analysis: Analyzed body proportions
            riding_preference: Riding preference type
            top_n: Number of recommendations to return
            
        Returns:
            List of tuples: (Motorcycle, overall_score, score_breakdown)
        """
        motorcycles = self.get_all_motorcycles()
        scored_bikes = []

        for bike in motorcycles:
            # Calculate individual scores
            seat_score = self.calculate_seat_height_score(
                body_analysis.inseam_cm,
                bike.seat_height_cm
            )
            weight_score = self.calculate_weight_score(
                weight_kg,
                bike.weight_kg
            )
            preference_score = self.calculate_preference_score(
                riding_preference,
                bike.riding_style
            )

            # Calculate overall score
            overall_score = self.calculate_overall_score(
                seat_score,
                weight_score,
                preference_score
            )

            scored_bikes.append((
                bike,
                overall_score,
                {
                    "seat_height": round(seat_score, 1),
                    "weight": round(weight_score, 1),
                    "ergonomics": round(preference_score, 1),
                    "overall": round(overall_score, 1)
                }
            ))

        # Sort by overall score and return top N
        scored_bikes.sort(key=lambda x: x[1], reverse=True)
        return scored_bikes[:top_n]

    def generate_recommendation_reason(
        self,
        bike: Motorcycle,
        body_analysis: BodyAnalysis,
        riding_preference: RidingPreference,
        score_breakdown: dict
    ) -> str:
        """
        Generate human-readable explanation for recommendation.
        
        Args:
            bike: Recommended motorcycle
            body_analysis: User body analysis
            riding_preference: Riding preference
            score_breakdown: Score breakdown by category
            
        Returns:
            Human-readable recommendation reason
        """
        reason = (
            f"The {bike.brand} {bike.name} is recommended for you because:\n"
        )

        # Seat height explanation
        seat_diff = abs(body_analysis.inseam_cm - bike.seat_height_cm)
        if seat_diff <= 5:
            reason += f"- Excellent seat height fit (inseam: {body_analysis.inseam_cm:.0f}cm, seat: {bike.seat_height_cm:.0f}cm)\n"
        else:
            reason += f"- Good seat height compatibility (within {seat_diff:.0f}cm of ideal)\n"

        # Weight explanation
        ratio = body_analysis.inseam_cm / bike.weight_kg
        if 0.5 <= ratio <= 1.5:
            reason += f"- Well-balanced weight-to-rider ratio for stable handling\n"
        else:
            reason += f"- Suitable weight distribution for your characteristics\n"

        # Preference explanation
        reason += f"- Perfect for {riding_preference.value} style riding\n"

        reason += f"- Overall suitability score: {score_breakdown['overall']:.0f}/100"

        return reason
