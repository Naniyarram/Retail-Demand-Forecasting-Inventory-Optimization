import logging
import os
import sys

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Console handler
    if not logger.handlers:
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        
    return logger

app_logger = setup_logger("retail_api")

class DriftDetector:
    def __init__(self):
        self.threshold = 0.50 # 50% deviation threshold
        # Hardcoding baseline train_mean for demo purposes; dynamically loadable via metrics.json in production
        self.train_mean = 20000.0 
        
    def check_drift(self, store_id: int, product_id: int, recent_sales: list) -> bool:
        if not recent_sales:
            return False
            
        live_mean = sum(recent_sales) / len(recent_sales)
        deviation = abs(live_mean - self.train_mean) / (self.train_mean + 1e-9)
        
        drift_flag = deviation > self.threshold
        
        if drift_flag:
            app_logger.warning(
                f"[DRIFT_ALERT] flag={drift_flag} | store_id={store_id} | product_id={product_id} "
                f"| stats: live={live_mean:.2f}, train={self.train_mean:.2f} | deviation={deviation:.2%}"
            )
        else:
            app_logger.info(
                f"[DRIFT_OK] store_id={store_id} | product_id={product_id} | live_mean={live_mean:.2f}"
            )
            
        return drift_flag

drift_detector = DriftDetector()
