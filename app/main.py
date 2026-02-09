import time
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
from app.service import face_service
from app.schemas import FaceVerificationResponse

app = FastAPI(
    title="Face Verification API - Enhanced with Advanced Preprocessing",
    description="""
    Robust face verification with ArcFace R100, multi-method verification, and manual review system.
    Optimized specifically for CNIC vs Selfie matching scenarios.
    """,
    version="3.0.0"
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
async def verify_faces(
    cnic_image: UploadFile = File(..., description="Upload CNIC/ID card image"),
    selfie_image: UploadFile = File(..., description="Upload Selfie picture")
):
    """
    Compare CNIC and Selfie images to verify identity.
    Uses multi-method verification (Cosine + Euclidean + Pearson) with quality compensation.
    
    Parameters:
    - cnic_image: CNIC/ID card photo (typically high quality, professional)
    - selfie_image: User's selfie photo (typically lower quality, user-submitted)
    
    The system automatically detects which image is higher quality and applies
    appropriate compensation for quality disparity.
    """
    start_time = time.time()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    
    # 1. Validate file types
    allowed_types = ["image/jpeg", "image/png", "image/webp"]
    if cnic_image.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"Invalid file type: {cnic_image.content_type}. Only JPEG/PNG/WebP allowed.")
    if selfie_image.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"Invalid file type: {selfie_image.content_type}. Only JPEG/PNG/WebP allowed.")
    
    # 2. Read image bytes
    try:
        cnic_bytes = await cnic_image.read()
        selfie_bytes = await selfie_image.read()
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to read image files.")

    # 3. Get Embeddings and Cropped Faces
    # Don't raise exceptions - handle gracefully
    try:
        emb1, count1, quality1, crop_method1 = face_service.get_embedding(cnic_bytes, "cnic")
        emb2, count2, quality2, crop_method2 = face_service.get_embedding(selfie_bytes, "selfie")
    except Exception as e:
        print(f"⚠️  Error processing images: {e}")
        # Return graceful error response instead of 400
        return FaceVerificationResponse(
            similarity_score=None,
            is_match=False,
            threshold_used=face_service.SIMILARITY_THRESHOLD,
            execution_time_ms=0,
            cosine_similarity=0,
            euclidean_similarity=0,
            pearson_similarity=0,
            quality_adjusted_score=0,
            image_quality_1=None,
            image_quality_2=None,
            average_quality=0,
            model_info={"name": "buffalo_l", "embedding_size": 512, "detector": "RetinaFace", "recognition": "ArcFace R50"},
            crop_info={
                "cnic_method": "error",
                "selfie_method": "error",
                "aligned_size": "112x112",
                "alignment_type": "affine_transform_5_landmarks"
            },
            faces_found_image_1=0,
            faces_found_image_2=0,
            confidence="LOW",
            needs_manual_review=False,
            review_reason="Image processing error",
            message=f"Error processing images: {str(e)}. Please ensure images are valid and contain visible faces."
        )
    
    # 4. Check results - Handle no face detected gracefully
    if emb1 is None or emb2 is None:
        # Determine which image(s) failed
        failed_images = []
        if emb1 is None:
            failed_images.append("CNIC")
        if emb2 is None:
            failed_images.append("Selfie")
        
        failed_str = " and ".join(failed_images)
        
        return FaceVerificationResponse(
            similarity_score=None,
            is_match=False,
            threshold_used=face_service.SIMILARITY_THRESHOLD,
            execution_time_ms=(time.time() - start_time) * 1000,
            cosine_similarity=0,
            euclidean_similarity=0,
            pearson_similarity=0,
            quality_adjusted_score=0,
            image_quality_1=quality1,
            image_quality_2=quality2,
            average_quality=0,
            model_info={"name": "buffalo_l", "embedding_size": 512, "detector": "RetinaFace", "recognition": "ArcFace R50"},
            crop_info={
                "cnic_method": crop_method1 if crop_method1 else "no_face_detected",
                "selfie_method": crop_method2 if crop_method2 else "no_face_detected",
                "aligned_size": "112x112",
                "alignment_type": "affine_transform_5_landmarks"
            },
            faces_found_image_1=count1,
            faces_found_image_2=count2,
            confidence="LOW",
            needs_manual_review=False,
            review_reason=f"No face detected in {failed_str} image(s)",
            message=f"⚠️ No face detected in {failed_str} image(s). The system tried 7 different detection methods including auto-rotation (for sideways/landscape CNIC images) but could not find a face. Please ensure: 1) Face is clearly visible, 2) Good lighting, 3) Face is not too small/distant, 4) Image is not blurry. The system automatically handles rotated images."
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
            message = "CNIC and Selfie match verified. High confidence."
        else:
            message = "CNIC and Selfie match verified."
    else:
        if confidence_result['needs_review']:
            message = f"Uncertain match - {confidence_result['reason']}. This case has been flagged for manual review."
        else:
            message = "CNIC and Selfie do not match. Please ensure good lighting and clear visibility."
    
    # 8. Save for Manual Review if Needed
    review_path = None
    if confidence_result['needs_review']:
        review_path = face_service.save_for_manual_review(
            cnic_bytes, 
            selfie_bytes,
            {
                'scores': verification_scores,
                'confidence': confidence_result,
                'quality1': quality1,
                'quality2': quality2,
                'crop_info': {'cnic': crop_method1, 'selfie': crop_method2},
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
        quality_adjusted_score=verification_scores['quality_adjusted_score'],
        selected_method=verification_scores.get('selected_method', 'unknown'),
        
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