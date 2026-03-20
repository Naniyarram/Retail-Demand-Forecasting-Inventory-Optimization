import math

class InventoryService:
    @staticmethod
    def calculate_reorder_decision(forecast: float, lead_time: int, service_level_z: float, 
                                   error_std: float, current_inventory: float) -> dict:
        
        forecast = max(0.0, forecast)
        current_inventory = max(0.0, current_inventory)
        
        # Safety Stock
        safety_stock = service_level_z * error_std * math.sqrt(lead_time)
        reorder_point = max(0.0, (forecast * lead_time) + safety_stock)
        
        # Gap Calculation
        # gap > 0 indicates Shortage. gap < 0 indicates Overstock.
        gap = reorder_point - current_inventory
        reorder_qty = max(0.0, gap)
        
        # Weeks of Inventory
        if forecast > 0:
            woi = current_inventory / forecast
        else:
            woi = None
            
        # Utilization and Benchmarking
        target_woi = "4-6"
        utilization = forecast / current_inventory if current_inventory > 0 else float('inf')
            
        # Action Decision Logic
        if current_inventory < reorder_point:
            action = "REORDER"
        elif woi is not None and woi > 12:
            action = "CRITICAL_OVERSTOCK"
        elif woi is not None and woi > 8:
            action = "OVERSTOCK"
        else:
            action = "OK"
            
        return {
            "reorder_point": round(reorder_point, 2),
            "recommended_reorder_qty": round(reorder_qty, 2),
            "inventory_gap": round(gap, 2),
            "weeks_of_inventory": round(woi, 2) if woi is not None else None,
            "target_woi": target_woi,
            "utilization": round(utilization, 4) if utilization != float('inf') else 0.0,
            "action": action
        }

inventory_service = InventoryService()
