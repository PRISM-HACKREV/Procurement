"""
Data loader for mock supplier JSON files
"""
import json
import os
from typing import List, Dict, Optional
from pathlib import Path


class SupplierDataLoader:
    """Loads and manages mock supplier data"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self._cache: Dict[str, List[dict]] = {}
        self._load_all_data()
    
    def _load_all_data(self):
        """Load all supplier JSON files into memory"""
        material_files = {
            "cement": "cement_suppliers_mock.json",
            "sand": "sand_suppliers_mock.json",
            "gravel": "gravel_suppliers_mock.json",
            "bricks": "bricks_suppliers_mock.json"
        }
        
        for material_id, filename in material_files.items():
            filepath = self.data_dir / filename
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    self._cache[material_id] = json.load(f)
            else:
                self._cache[material_id] = []
    
    def get_suppliers_by_material(self, material_id: str) -> List[dict]:
        """
        Get all suppliers for a specific material.
        
        Args:
            material_id: Material identifier (cement, sand, gravel, bricks)
        
        Returns:
            List of supplier dictionaries
        """
        return self._cache.get(material_id, []).copy()
    
    def get_supplier_by_id(self, supplier_id: str) -> Optional[dict]:
        """
        Get a specific supplier by ID.
        
        Args:
            supplier_id: Unique supplier identifier
        
        Returns:
            Supplier dictionary or None if not found
        """
        for suppliers in self._cache.values():
            for supplier in suppliers:
                if supplier['supplier_id'] == supplier_id:
                    return supplier.copy()
        return None
    
    def get_all_materials(self) -> List[str]:
        """Get list of all available materials"""
        return list(self._cache.keys())
    
    def reload(self):
        """Reload all data from disk"""
        self._cache.clear()
        self._load_all_data()


# Global singleton instance
_loader_instance: Optional[SupplierDataLoader] = None


def get_data_loader() -> SupplierDataLoader:
    """Get or create the global data loader instance"""
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = SupplierDataLoader()
    return _loader_instance

