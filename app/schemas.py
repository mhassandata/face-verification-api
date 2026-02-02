from pydantic import BaseModel, Field
from typing import Optional, Dict

class FaceVerificationResponse(BaseModel):
    # Primary decision fields
    similarity_score: Optional[float] = Field(..., description="Primary similarity score (ensemble) between 0 and 1, or null if not calculated")
    is_match: bool = Field(..., description="Boolean decision based on threshold")
    threshold_used: float = Field(..., description="The threshold used for the decision")
    execution_time_ms: float = Field(..., description="Processing time in milliseconds")
    
    # Confidence and review fields
    confidence: Optional[str] = Field(None, description="Confidence level: HIGH, MEDIUM_HIGH, MEDIUM, LOW_MEDIUM, LOW")
    needs_manual_review: bool = Field(False, description="Whether this case needs manual review")
    review_reason: Optional[str] = Field(None, description="Reason for review or decision")
    
    # Multi-method verification scores
    cosine_similarity: Optional[float] = Field(None, description="Cosine similarity score")
    euclidean_similarity: Optional[float] = Field(None, description="Euclidean distance-based similarity")
    ensemble_score: Optional[float] = Field(None, description="Weighted ensemble of multiple methods")
    quality_adjusted_score: Optional[float] = Field(None, description="Score adjusted for image quality")
    
    # Quality metrics
    image_quality_1: Optional[Dict] = Field(None, description="Quality assessment for image 1")
    image_quality_2: Optional[Dict] = Field(None, description="Quality assessment for image 2")
    average_quality: Optional[float] = Field(None, description="Average quality score (0-1)")
    
    # Metadata about detections
    faces_found_image_1: int
    faces_found_image_2: int
    message: Optional[str] = None
    
    # Manual review path (if applicable)
    review_path: Optional[str] = Field(None, description="Path to manual review folder if flagged")
