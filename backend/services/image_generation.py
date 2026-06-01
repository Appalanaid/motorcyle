"""
AI image generation service using OpenAI DALL-E API.
Generates photorealistic images of user with recommended motorcycle.
"""

import base64
import requests
from typing import Optional
from config import get_settings
from models import Motorcycle


class ImageGenerationService:
    """
    Generates AI images of users with their recommended motorcycles.
    Uses OpenAI's DALL-E 3 API for high-quality image generation.
    """

    def __init__(self):
        """Initialize with OpenAI API configuration."""
        self.settings = get_settings()
        self.api_key = self.settings.openai_api_key
        self.model = self.settings.openai_model_image
        self.api_url = "https://api.openai.com/v1/images/generations"

    def generate_prompt(
        self,
        bike: Motorcycle,
        height_cm: float,
        weight_kg: float,
        posture_type: str
    ) -> str:
        """
        Generate detailed prompt for AI image generation.
        Includes motorcycle details and rider characteristics.
        
        Args:
            bike: Recommended motorcycle
            height_cm: Rider height
            weight_kg: Rider weight
            posture_type: Posture type (upright/sport/cruiser)
            
        Returns:
            Detailed prompt for DALL-E
        """
        # Build physical description based on height/weight
        bmi = weight_kg / ((height_cm / 100) ** 2)
        if bmi < 18.5:
            build = "lean"
        elif bmi < 25:
            build = "athletic"
        elif bmi < 30:
            build = "muscular"
        else:
            build = "sturdy"

        # Height category
        if height_cm < 160:
            height_desc = "short"
        elif height_cm < 175:
            height_desc = "average height"
        else:
            height_desc = "tall"

        # Posture description for riding position
        posture_desc = {
            "upright": "upright, comfortable riding position",
            "sporty": "forward-leaning, aggressive riding position",
            "cruiser": "relaxed, laid-back cruising position"
        }.get(posture_type, "comfortable riding position")

        prompt = (
            f"Professional photograph of a {height_desc}, {build} person "
            f"riding a {bike.brand} {bike.name} motorcycle "
            f"in a {posture_desc}. "
            f"The motorcycle is a {bike.riding_style} style bike "
            f"with a {bike.seat_height_cm}cm seat height. "
            f"The rider is confidently gripping the handlebars, "
            f"engaged with the bike. "
            f"Professional lighting, clear day, outdoor setting, "
            f"realistic photography, high quality, detailed, vibrant colors. "
            f"The rider and motorcycle are perfectly proportioned and well-suited. "
            f"4K resolution, cinematic quality."
        )

        return prompt

    def generate_image(
        self,
        bike: Motorcycle,
        height_cm: float,
        weight_kg: float,
        posture_type: str,
        size: str = "1024x1024"
    ) -> Optional[str]:
        """
        Generate AI image of rider with motorcycle.
        
        Args:
            bike: Recommended motorcycle
            height_cm: Rider height
            weight_kg: Rider weight
            posture_type: Posture type
            size: Image size (1024x1024, 1792x1024, 1024x1792)
            
        Returns:
            Image URL from OpenAI or None if generation fails
        """
        if not self.api_key:
            print("Warning: OpenAI API key not configured")
            return None

        try:
            prompt = self.generate_prompt(bike, height_cm, weight_kg, posture_type)

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": self.model,
                "prompt": prompt,
                "n": 1,
                "size": size,
                "quality": "hd",
                "style": "natural"
            }

            response = requests.post(
                self.api_url,
                json=data,
                headers=headers,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                image_url = result["data"][0]["url"]
                print(f"Image generated successfully: {image_url}")
                return image_url
            else:
                print(f"Image generation failed: {response.status_code}")
                print(f"Response: {response.text}")
                return None

        except requests.RequestException as e:
            print(f"Request error during image generation: {e}")
            return None
        except Exception as e:
            print(f"Error generating image: {e}")
            return None

    def save_image_locally(self, image_url: str, filename: str) -> bool:
        """
        Download and save generated image locally.
        
        Args:
            image_url: URL of generated image
            filename: Local filepath to save image
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.get(image_url, timeout=30)
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"Image saved to {filename}")
                return True
        except Exception as e:
            print(f"Error saving image: {e}")
            return False


# Global service instance
_gen_service: Optional[ImageGenerationService] = None


def get_image_generation_service() -> ImageGenerationService:
    """Get or create image generation service instance."""
    global _gen_service
    if _gen_service is None:
        _gen_service = ImageGenerationService()
    return _gen_service
