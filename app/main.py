import time
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
from app.service import face_service
from app.schemas import FaceVerificationResponse

app = FastAPI(
    title="Face Verification API - Enhanced (antelopev2)",
    description="Robust face verification with ArcFace R100, multi-method verification, and manual review system. Optimized for CNIC vs Selfie matching.",
    version="2.1.0"
)

# Validate file types
ALLOWED_EXTENSIONS = {"image/jpeg", "image/png", "image/jpg", "image/webp"}

def validate_image(file: UploadFile):
    if file.content_type not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type: {file.content_type}. Only JPEG/PNG/WebP allowed."
        )

@app.post("/verify", response_model=FaceVerificationResponse)
def verify_faces(
    source_image: UploadFile = File(...),
    target_image: UploadFile = File(...)
):
    """
    Upload two images to verify if they belong to the same person.
    
    **Enhanced Features:**
    - Multi-method verification (Cosine + Euclidean + Ensemble)
    - Image quality assessment
    - Confidence level determination
    - Automatic manual review flagging for edge cases
    
    **Parameters:**
    - **source_image**: Reference image (CNIC, ID card, etc.)
    - **target_image**: Image to verify (Selfie, etc.)
    
    **Response includes:**
    - Primary similarity score (ensemble of multiple methods)
    - Individual method scores (cosine, euclidean)
    - Confidence level (HIGH, MEDIUM_HIGH, MEDIUM, LOW_MEDIUM, LOW)
    - Manual review flag for uncertain cases
    - Image quality metrics
    """
    start_time = time.time()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

    # 1. Validation
    validate_image(source_image)
    validate_image(target_image)

    # 2. Read Bytes
    try:
        source_bytes = source_image.file.read()
        target_bytes = target_image.file.read()
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to read image files.")

    # 3. Process Images with Quality Assessment
    try:
        emb1, count1, quality1 = face_service.get_embedding(source_bytes, image_label="source")
        emb2, count2, quality2 = face_service.get_embedding(target_bytes, image_label="target")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 4. Handle "No Face Found" - treat as failed match
    if emb1 is None or emb2 is None:
        execution_time = (time.time() - start_time) * 1000
        return FaceVerificationResponse(
            similarity_score=None,
            is_match=False,
            threshold_used=face_service.SIMILARITY_THRESHOLD,
            execution_time_ms=round(execution_time, 2),
            confidence="LOW",
            needs_manual_review=False,
            review_reason="No face detected in one or both images",
            faces_found_image_1=count1,
            faces_found_image_2=count2,
            message="Your picture is not clear or the faces do not match. Please ensure good lighting and clear visibility."
        )

    # 5. Multi-Method Verification
    verification_scores = face_service.multi_method_verification(emb1, emb2, quality1, quality2)
    
    # Use ensemble score as primary
    primary_score = verification_scores['primary_score']
    
    # 6. Determine Confidence Level and Review Necessity
    confidence_result = face_service.determine_confidence_level(primary_score, quality1, quality2)
    
    execution_time = (time.time() - start_time) * 1000
    
    # 7. Set appropriate message based on confidence and match result
    if confidence_result['is_match']:
        if confidence_result['confidence'] == 'HIGH':
            message = "Both pictures you provided are match. High confidence verification."
        else:
            message = "Both pictures you provided are match."
    else:
        if confidence_result['needs_review']:
            message = f"Uncertain match - {confidence_result['reason']}. This case has been flagged for manual review."
        else:
            message = "Your picture is not clear or the faces do not match. Please ensure good lighting and clear visibility."
    
    # 8. Save for Manual Review if Needed
    review_path = None
    if confidence_result['needs_review']:
        review_path = face_service.save_for_manual_review(
            source_bytes, 
            target_bytes,
            {
                'scores': verification_scores,
                'confidence': confidence_result,
                'quality1': quality1,
                'quality2': quality2,
                'timestamp': timestamp
            },
            timestamp
        )
        print(f"⚠️  MANUAL REVIEW REQUIRED: Case saved to {review_path}")

    return FaceVerificationResponse(
        # Primary fields
        similarity_score=primary_score,
        is_match=confidence_result['is_match'],
        threshold_used=face_service.SIMILARITY_THRESHOLD,
        execution_time_ms=round(execution_time, 2),
        
        # Confidence and review
        confidence=confidence_result['confidence'],
        needs_manual_review=confidence_result['needs_review'],
        review_reason=confidence_result['reason'],
        
        # Multi-method scores
        cosine_similarity=verification_scores['cosine_similarity'],
        euclidean_similarity=verification_scores['euclidean_similarity'],
        pearson_similarity=verification_scores['pearson_similarity'],
        ensemble_score=verification_scores['ensemble_score'],
        quality_adjusted_score=verification_scores['quality_adjusted_score'],
        
        # Quality metrics
        image_quality_1=quality1,
        image_quality_2=quality2,
        average_quality=verification_scores['avg_quality'],
        
        # Metadata
        faces_found_image_1=count1,
        faces_found_image_2=count2,
        message=message,
        review_path=review_path
    )


@app.get("/health")
def health_check():
    return {"status": "healthy", "model": "insightface-buffalo_l"}