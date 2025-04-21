import os
import json
import time
import threading
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

class TrainingManager:
    """Manages the training, testing, and improvement of AI models."""
    
    def __init__(self, model_dir: str = "models", logs_dir: str = "logs"):
        self.model_dir = model_dir
        self.logs_dir = logs_dir
        self.progress = {
            "training_model": 0,
            "testing_model": 0,
            "fixing_model": 0,
            "retesting_model": 0,
            "getting_ready": 0,
            "in_use": False,
            "continuous_learning": 0
        }
        self.current_stage = "idle"
        self.training_thread = None
        self.is_training = False
        self.training_history = []
        
        # Create directories if they don't exist
        os.makedirs(model_dir, exist_ok=True)
        os.makedirs(logs_dir, exist_ok=True)
        
        # Load training history if it exists
        self._load_training_history()
    
    def _load_training_history(self):
        """Load training history from logs."""
        history_path = os.path.join(self.logs_dir, "training_history.json")
        if os.path.exists(history_path):
            try:
                with open(history_path, 'r') as f:
                    self.training_history = json.load(f)
            except Exception as e:
                print(f"Error loading training history: {e}")
                self.training_history = []
    
    def _save_training_history(self):
        """Save training history to logs."""
        history_path = os.path.join(self.logs_dir, "training_history.json")
        try:
            with open(history_path, 'w') as f:
                json.dump(self.training_history, f)
        except Exception as e:
            print(f"Error saving training history: {e}")
    
    def start_training(self, model_name: str, dataset_path: str, params: Dict = None):
        """Start the training pipeline in a separate thread."""
        if self.is_training:
            return {"status": "error", "message": "Training already in progress"}
        
        self.is_training = True
        self.current_stage = "training_model"
        self.progress = {key: 0 for key in self.progress}
        self.progress["in_use"] = False
        
        # Start training in a separate thread
        self.training_thread = threading.Thread(
            target=self._training_pipeline,
            args=(model_name, dataset_path, params)
        )
        self.training_thread.start()
        
        return {"status": "success", "message": "Training started"}
    
    def _training_pipeline(self, model_name: str, dataset_path: str, params: Dict = None):
        """Execute the full training pipeline."""
        try:
            # Record start time
            start_time = time.time()
            training_record = {
                "model_name": model_name,
                "start_time": datetime.now().isoformat(),
                "stages": {}
            }
            
            # 1. Training model
            self.current_stage = "training_model"
            training_record["stages"]["training"] = self._train_model(model_name, dataset_path, params)
            
            # 2. Testing model
            self.current_stage = "testing_model"
            test_results = self._test_model(model_name)
            training_record["stages"]["testing"] = test_results
            
            # 3. Fixing model if needed
            if test_results["accuracy"] < 0.85:  # Threshold for acceptable accuracy
                self.current_stage = "fixing_model"
                training_record["stages"]["fixing"] = self._fix_model(model_name, dataset_path, test_results)
                
                # 4. Retesting after fixes
                self.current_stage = "retesting_model"
                retest_results = self._test_model(model_name)
                training_record["stages"]["retesting"] = retest_results
            
            # 5. Getting model ready
            self.current_stage = "getting_ready"
            self._prepare_model_for_use(model_name)
            
            # 6. Model is in use
            self.current_stage = "in_use"
            self.progress["in_use"] = True
            
            # Record end time and save history
            training_record["end_time"] = datetime.now().isoformat()
            training_record["duration"] = time.time() - start_time
            training_record["success"] = True
            
            self.training_history.append(training_record)
            self._save_training_history()
            
        except Exception as e:
            print(f"Error in training pipeline: {e}")
            training_record = {
                "model_name": model_name,
                "start_time": datetime.now().isoformat(),
                "end_time": datetime.now().isoformat(),
                "error": str(e),
                "success": False
            }
            self.training_history.append(training_record)
            self._save_training_history()
        
        finally:
            self.is_training = False
            self.current_stage = "idle"
    
    def _train_model(self, model_name: str, dataset_path: str, params: Dict = None) -> Dict:
        """Train the model and update progress."""
        # Simulate training or implement actual training logic
        total_epochs = params.get("epochs", 10) if params else 10
        
        results = {"accuracy": 0, "loss": 0}
        
        for epoch in range(total_epochs):
            # Update progress
            self.progress["training_model"] = int((epoch + 1) / total_epochs * 100)
            
            # Simulate or implement actual epoch training
            time.sleep(0.5)  # Simulate training time
            
            # Update results
            results["accuracy"] = (epoch + 1) / total_epochs * 0.9  # Simulated accuracy
            results["loss"] = 1 - results["accuracy"]
        
        # Save model
        model_path = os.path.join(self.model_dir, f"{model_name}.model")
        with open(model_path, 'w') as f:
            json.dump({"trained": True, "params": params}, f)
        
        return results
    
    def _test_model(self, model_name: str) -> Dict:
        """Test the model and update progress."""
        # Simulate testing or implement actual testing logic
        for i in range(10):
            self.progress["testing_model"] = (i + 1) * 10
            time.sleep(0.2)  # Simulate testing time
        
        # Simulated test results
        return {
            "accuracy": 0.82,
            "precision": 0.85,
            "recall": 0.80,
            "f1_score": 0.82
        }
    
    def _fix_model(self, model_name: str, dataset_path: str, test_results: Dict) -> Dict:
        """Fix model issues and update progress."""
        # Determine what needs fixing based on test results
        if test_results["accuracy"] < 0.7:
            # Major issues - retrain from scratch with more data
            for i in range(20):
                self.progress["fixing_model"] = (i + 1) * 5
                time.sleep(0.3)  # Simulate fixing time
            
            # Retrain with adjusted parameters
            return self._train_model(model_name, dataset_path, {"epochs": 15})
        else:
            # Minor issues - fine-tune
            for i in range(10):
                self.progress["fixing_model"] = (i + 1) * 10
                time.sleep(0.2)  # Simulate fixing time
            
            return {"accuracy": 0.88, "loss": 0.12}
    
    def _prepare_model_for_use(self, model_name: str):
        """Prepare the model for production use."""
        for i in range(10):
            self.progress["getting_ready"] = (i + 1) * 10
            time.sleep(0.1)  # Simulate preparation time
    
    def get_progress(self) -> Dict:
        """Get the current training progress."""
        return {
            "stage": self.current_stage,
            "progress": self.progress,
            "is_training": self.is_training
        }
    
    def start_continuous_learning(self, model_name: str):
        """Start continuous learning from user interactions."""
        if not self.progress["in_use"]:
            return {"status": "error", "message": "Model must be in use to start continuous learning"}
        
        # Start continuous learning thread
        threading.Thread(
            target=self._continuous_learning_loop,
            args=(model_name,),
            daemon=True
        ).start()
        
        return {"status": "success", "message": "Continuous learning started"}
    
    def _continuous_learning_loop(self, model_name: str):
        """Continuously learn from new data."""
        while self.progress["in_use"]:
            # Simulate learning from recent interactions
            self.progress["continuous_learning"] = (self.progress["continuous_learning"] + 1) % 100
            time.sleep(5)  # Check for new data every 5 seconds
