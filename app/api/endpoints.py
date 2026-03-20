from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.requests import ForecastRequest, ReorderRequest, BatchPredictRequest
from app.schemas.responses import ForecastResponse, ReorderResponse
from app.services.forecast_service import forecast_service
from app.services.inventory_service import inventory_service
from app.core.logging import app_logger, drift_detector

router = APIRouter()

def validate_history(recent_sales: List[float]):
    if not recent_sales:
        app_logger.warning("[COLD_START] Missing recent_sales history, generating default fallback projection.")
        return False
    if len(recent_sales) < 7:
        app_logger.warning(f"[INSUFFICIENT_DATA] recent_sales len={len(recent_sales)} vs required=7. Padding or fallback logic needed.")
        return False
    return True

@router.post("/predict", response_model=ForecastResponse)
async def predict(request: ForecastRequest):
    try:
        app_logger.info(f"[REQUEST] /predict -> store_id={request.store_id}, product_id={request.product_id}")
        
        # Validation and Cold Start Check
        has_history = validate_history(request.recent_sales)
        if not has_history:
            # Fallback average
            forecast = 15000.0
        else:
            drift_detector.check_drift(request.store_id, request.product_id, request.recent_sales)
            forecast = forecast_service.predict(
                store_id=request.store_id,
                product_id=request.product_id,
                date=request.date,
                recent_sales=request.recent_sales
            )

        return ForecastResponse(
            store_id=request.store_id,
            product_id=request.product_id,
            date=request.date,
            forecast=forecast
        )
    except ValueError as ve:
        app_logger.error(f"[ERROR] ValueError: {str(ve)}")
        raise HTTPException(status_code=400, detail={"error": "Invalid input", "message": str(ve)})
    except Exception as e:
        app_logger.error(f"[ERROR] ServerError: {str(e)}")
        raise HTTPException(status_code=500, detail={"error": "Server exception", "message": str(e)})

@router.post("/reorder-decision", response_model=ReorderResponse)
async def reorder_decision(request: ReorderRequest):
    try:
        app_logger.info(f"[REQUEST] /reorder-decision -> store_id={request.store_id}, product_id={request.product_id}")
        
        has_history = validate_history(request.recent_sales)
        if not has_history:
            forecast = 15000.0
        else:
            drift_detector.check_drift(request.store_id, request.product_id, request.recent_sales)
            forecast = forecast_service.predict(
                store_id=request.store_id,
                product_id=request.product_id,
                date=request.date,
                recent_sales=request.recent_sales
            )
        
        decision = inventory_service.calculate_reorder_decision(
            forecast=forecast,
            lead_time=request.lead_time,
            service_level_z=request.service_level_z,
            error_std=request.error_std,
            current_inventory=request.current_inventory
        )
        
        return ReorderResponse(
            store_id=request.store_id,
            product_id=request.product_id,
            date=request.date,
            forecast=forecast,
            **decision
        )
    except ValueError as ve:
        app_logger.error(f"[ERROR] ValueError: {str(ve)}")
        raise HTTPException(status_code=400, detail={"error": "Invalid input", "message": str(ve)})
    except Exception as e:
        app_logger.error(f"[ERROR] ServerError: {str(e)}")
        raise HTTPException(status_code=500, detail={"error": "Server exception", "message": str(e)})

@router.post("/predict-batch", response_model=List[ForecastResponse])
async def predict_batch(batch_req: BatchPredictRequest):
    app_logger.info(f"[REQUEST] /predict-batch -> Received {len(batch_req.requests)} items")
    responses = []
    for req in batch_req.requests:
        try:
            has_history = validate_history(req.recent_sales)
            if not has_history:
                forecast = 15000.0
            else:
                forecast = forecast_service.predict(req.store_id, req.product_id, req.date, req.recent_sales)
            responses.append(ForecastResponse(
                store_id=req.store_id,
                product_id=req.product_id,
                date=req.date,
                forecast=forecast
            ))
        except Exception as e:
            app_logger.error(f"Batch prediction failure for item: {str(e)}")
            # Skip failed or return 0
            responses.append(ForecastResponse(store_id=req.store_id, product_id=req.product_id, date=req.date, forecast=0.0))
    return responses
