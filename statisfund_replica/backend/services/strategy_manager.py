import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import hashlib
import uuid

class StrategyManager:
    """Strategy management system for saving, loading, and versioning strategies"""
    
    def __init__(self, storage_path: str = "strategies"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.storage_path / "active").mkdir(exist_ok=True)
        (self.storage_path / "archived").mkdir(exist_ok=True)
        (self.storage_path / "templates").mkdir(exist_ok=True)
        
    def save_strategy(self, strategy_data: Dict[str, Any]) -> str:
        """Save a strategy and return its ID"""
        
        strategy_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # Generate code hash for version control
        code_hash = hashlib.md5(strategy_data['code'].encode()).hexdigest()
        
        strategy_record = {
            'id': strategy_id,
            'name': strategy_data.get('name', f"Strategy_{strategy_id[:8]}"),
            'description': strategy_data.get('description', ''),
            'code': strategy_data['code'],
            'symbols': strategy_data.get('symbols', []),
            'parameters': strategy_data.get('parameters', {}),
            'backtest_config': strategy_data.get('backtest_config', {}),
            'performance_metrics': strategy_data.get('performance_metrics', {}),
            'validation_results': strategy_data.get('validation_results', {}),
            'created_at': timestamp,
            'updated_at': timestamp,
            'version': 1,
            'code_hash': code_hash,
            'status': 'active',
            'tags': strategy_data.get('tags', []),
            'author': strategy_data.get('author', 'unknown'),
            'category': strategy_data.get('category', 'custom')
        }
        
        # Save to file
        file_path = self.storage_path / "active" / f"{strategy_id}.json"
        with open(file_path, 'w') as f:
            json.dump(strategy_record, f, indent=2)
        
        return strategy_id
    
    def load_strategy(self, strategy_id: str) -> Optional[Dict[str, Any]]:
        """Load a strategy by ID"""
        
        # Check active strategies first
        file_path = self.storage_path / "active" / f"{strategy_id}.json"
        if file_path.exists():
            with open(file_path, 'r') as f:
                return json.load(f)
        
        # Check archived strategies
        file_path = self.storage_path / "archived" / f"{strategy_id}.json"
        if file_path.exists():
            with open(file_path, 'r') as f:
                return json.load(f)
        
        return None
    
    def update_strategy(self, strategy_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing strategy"""
        
        strategy = self.load_strategy(strategy_id)
        if not strategy:
            return False
        
        # Update fields
        for key, value in updates.items():
            if key not in ['id', 'created_at', 'version']:
                strategy[key] = value
        
        # Update metadata
        strategy['updated_at'] = datetime.now().isoformat()
        
        # Check if code changed
        if 'code' in updates:
            new_hash = hashlib.md5(updates['code'].encode()).hexdigest()
            if new_hash != strategy['code_hash']:
                strategy['version'] += 1
                strategy['code_hash'] = new_hash
        
        # Save updated strategy
        file_path = self.storage_path / "active" / f"{strategy_id}.json"
        with open(file_path, 'w') as f:
            json.dump(strategy, f, indent=2)
        
        return True
    
    def list_strategies(self, status: str = "active", category: Optional[str] = None, 
                       tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """List strategies with optional filtering"""
        
        strategies = []
        search_path = self.storage_path / status
        
        if not search_path.exists():
            return strategies
        
        for file_path in search_path.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    strategy = json.load(f)
                
                # Apply filters
                if category and strategy.get('category') != category:
                    continue
                
                if tags:
                    strategy_tags = strategy.get('tags', [])
                    if not any(tag in strategy_tags for tag in tags):
                        continue
                
                # Remove code from listing for performance
                strategy_summary = {k: v for k, v in strategy.items() if k != 'code'}
                strategies.append(strategy_summary)
                
            except Exception as e:
                print(f"Error loading strategy {file_path}: {e}")
        
        # Sort by updated_at descending
        strategies.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
        
        return strategies
    
    def archive_strategy(self, strategy_id: str) -> bool:
        """Archive a strategy (move from active to archived)"""
        
        active_path = self.storage_path / "active" / f"{strategy_id}.json"
        archived_path = self.storage_path / "archived" / f"{strategy_id}.json"
        
        if not active_path.exists():
            return False
        
        # Load and update status
        with open(active_path, 'r') as f:
            strategy = json.load(f)
        
        strategy['status'] = 'archived'
        strategy['archived_at'] = datetime.now().isoformat()
        
        # Move to archived
        with open(archived_path, 'w') as f:
            json.dump(strategy, f, indent=2)
        
        # Remove from active
        active_path.unlink()
        
        return True
    
    def delete_strategy(self, strategy_id: str) -> bool:
        """Permanently delete a strategy"""
        
        # Check both active and archived
        for folder in ["active", "archived"]:
            file_path = self.storage_path / folder / f"{strategy_id}.json"
            if file_path.exists():
                file_path.unlink()
                return True
        
        return False
    
    def search_strategies(self, query: str, status: str = "active") -> List[Dict[str, Any]]:
        """Search strategies by name, description, or tags"""
        
        strategies = self.list_strategies(status=status)
        query_lower = query.lower()
        
        matching_strategies = []
        
        for strategy in strategies:
            # Search in name
            if query_lower in strategy.get('name', '').lower():
                matching_strategies.append(strategy)
                continue
            
            # Search in description
            if query_lower in strategy.get('description', '').lower():
                matching_strategies.append(strategy)
                continue
            
            # Search in tags
            tags = strategy.get('tags', [])
            if any(query_lower in tag.lower() for tag in tags):
                matching_strategies.append(strategy)
                continue
        
        return matching_strategies
    
    def get_strategy_performance(self, strategy_id: str) -> Optional[Dict[str, Any]]:
        """Get performance metrics for a strategy"""
        
        strategy = self.load_strategy(strategy_id)
        if not strategy:
            return None
        
        return strategy.get('performance_metrics', {})
    
    def update_strategy_performance(self, strategy_id: str, performance_data: Dict[str, Any]) -> bool:
        """Update strategy performance metrics"""
        
        return self.update_strategy(strategy_id, {
            'performance_metrics': performance_data,
            'last_backtest': datetime.now().isoformat()
        })
    
    def create_strategy_template(self, template_data: Dict[str, Any]) -> str:
        """Create a reusable strategy template"""
        
        template_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        template_record = {
            'id': template_id,
            'name': template_data['name'],
            'description': template_data.get('description', ''),
            'code_template': template_data['code_template'],
            'parameters': template_data.get('parameters', {}),
            'category': template_data.get('category', 'template'),
            'created_at': timestamp,
            'usage_count': 0,
            'tags': template_data.get('tags', [])
        }
        
        # Save template
        file_path = self.storage_path / "templates" / f"{template_id}.json"
        with open(file_path, 'w') as f:
            json.dump(template_record, f, indent=2)
        
        return template_id
    
    def get_strategy_templates(self) -> List[Dict[str, Any]]:
        """Get all available strategy templates"""
        
        templates = []
        templates_path = self.storage_path / "templates"
        
        for file_path in templates_path.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    template = json.load(f)
                templates.append(template)
            except Exception as e:
                print(f"Error loading template {file_path}: {e}")
        
        return sorted(templates, key=lambda x: x.get('usage_count', 0), reverse=True)
    
    def create_from_template(self, template_id: str, strategy_data: Dict[str, Any]) -> Optional[str]:
        """Create a new strategy from a template"""
        
        template_path = self.storage_path / "templates" / f"{template_id}.json"
        if not template_path.exists():
            return None
        
        with open(template_path, 'r') as f:
            template = json.load(f)
        
        # Create strategy from template
        new_strategy = {
            'name': strategy_data.get('name', template['name']),
            'description': strategy_data.get('description', template['description']),
            'code': template['code_template'],
            'parameters': {**template.get('parameters', {}), **strategy_data.get('parameters', {})},
            'category': 'from_template',
            'template_id': template_id,
            'tags': strategy_data.get('tags', template.get('tags', []))
        }
        
        # Update template usage count
        template['usage_count'] = template.get('usage_count', 0) + 1
        with open(template_path, 'w') as f:
            json.dump(template, f, indent=2)
        
        return self.save_strategy(new_strategy)
    
    def export_strategy(self, strategy_id: str, include_performance: bool = True) -> Optional[Dict[str, Any]]:
        """Export strategy for sharing or backup"""
        
        strategy = self.load_strategy(strategy_id)
        if not strategy:
            return None
        
        export_data = {
            'name': strategy['name'],
            'description': strategy['description'],
            'code': strategy['code'],
            'parameters': strategy['parameters'],
            'symbols': strategy['symbols'],
            'tags': strategy['tags'],
            'category': strategy['category'],
            'version': strategy['version'],
            'exported_at': datetime.now().isoformat()
        }
        
        if include_performance:
            export_data['performance_metrics'] = strategy.get('performance_metrics', {})
            export_data['validation_results'] = strategy.get('validation_results', {})
        
        return export_data
    
    def import_strategy(self, import_data: Dict[str, Any], author: str = "imported") -> str:
        """Import a strategy from export data"""
        
        strategy_data = {
            'name': import_data['name'],
            'description': import_data['description'],
            'code': import_data['code'],
            'parameters': import_data.get('parameters', {}),
            'symbols': import_data.get('symbols', []),
            'tags': import_data.get('tags', []) + ['imported'],
            'category': import_data.get('category', 'imported'),
            'author': author,
            'performance_metrics': import_data.get('performance_metrics', {}),
            'validation_results': import_data.get('validation_results', {})
        }
        
        return self.save_strategy(strategy_data)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics about strategies"""
        
        active_strategies = self.list_strategies(status="active")
        archived_strategies = self.list_strategies(status="archived")
        templates = self.get_strategy_templates()
        
        # Category distribution
        categories = {}
        for strategy in active_strategies:
            cat = strategy.get('category', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        # Performance statistics
        total_returns = []
        sharpe_ratios = []
        
        for strategy in active_strategies:
            perf = strategy.get('performance_metrics', {})
            if 'total_return' in perf:
                total_returns.append(perf['total_return'])
            if 'sharpe_ratio' in perf:
                sharpe_ratios.append(perf['sharpe_ratio'])
        
        stats = {
            'total_strategies': len(active_strategies) + len(archived_strategies),
            'active_strategies': len(active_strategies),
            'archived_strategies': len(archived_strategies),
            'templates': len(templates),
            'categories': categories,
            'performance_stats': {
                'strategies_with_performance': len(total_returns),
                'avg_return': sum(total_returns) / len(total_returns) if total_returns else 0,
                'avg_sharpe': sum(sharpe_ratios) / len(sharpe_ratios) if sharpe_ratios else 0,
                'best_return': max(total_returns) if total_returns else 0,
                'worst_return': min(total_returns) if total_returns else 0
            }
        }
        
        return stats
