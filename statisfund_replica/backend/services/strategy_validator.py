import ast
import re
from typing import Dict, List, Any, Tuple
from datetime import datetime
import inspect

class StrategyValidator:
    """Comprehensive strategy validation and safety checking"""
    
    def __init__(self):
        self.dangerous_imports = {
            'os', 'sys', 'subprocess', 'socket', 'urllib', 'requests',
            'pickle', 'marshal', 'shelve', 'dbm', 'sqlite3',
            'threading', 'multiprocessing', 'asyncio', 'concurrent',
            'ctypes', 'importlib', '__builtin__', 'builtins'
        }
        
        self.dangerous_functions = {
            'exec', 'eval', 'compile', 'open', 'file', 'input', 'raw_input',
            'globals', 'locals', 'vars', 'dir', 'getattr', 'setattr', 
            'delattr', 'hasattr', '__import__', 'reload'
        }
        
        self.required_methods = ['__init__', 'next']
        self.recommended_methods = ['log', 'notify_order', 'notify_trade']
        
    def validate_strategy_code(self, code: str) -> Dict[str, Any]:
        """Comprehensive validation of strategy code"""
        
        validation_result = {
            'is_valid': False,
            'errors': [],
            'warnings': [],
            'security_issues': [],
            'recommendations': [],
            'metrics': {}
        }
        
        try:
            # 1. Syntax validation
            syntax_errors = self._validate_syntax(code)
            if syntax_errors:
                validation_result['errors'].extend(syntax_errors)
                return validation_result
            
            # 2. Security validation
            security_issues = self._validate_security(code)
            validation_result['security_issues'] = security_issues
            
            # 3. Structure validation
            structure_errors, structure_warnings = self._validate_structure(code)
            validation_result['errors'].extend(structure_errors)
            validation_result['warnings'].extend(structure_warnings)
            
            # 4. Risk management validation
            risk_warnings = self._validate_risk_management(code)
            validation_result['warnings'].extend(risk_warnings)
            
            # 5. Performance validation
            performance_warnings = self._validate_performance(code)
            validation_result['warnings'].extend(performance_warnings)
            
            # 6. Generate recommendations
            recommendations = self._generate_recommendations(code)
            validation_result['recommendations'] = recommendations
            
            # 7. Calculate metrics
            metrics = self._calculate_code_metrics(code)
            validation_result['metrics'] = metrics
            
            # Final validation status
            validation_result['is_valid'] = (
                len(validation_result['errors']) == 0 and 
                len(validation_result['security_issues']) == 0
            )
            
        except Exception as e:
            validation_result['errors'].append(f"Validation failed: {str(e)}")
        
        return validation_result
    
    def _validate_syntax(self, code: str) -> List[str]:
        """Validate Python syntax"""
        errors = []
        
        try:
            ast.parse(code)
        except SyntaxError as e:
            errors.append(f"Syntax error at line {e.lineno}: {e.msg}")
        except Exception as e:
            errors.append(f"Code parsing error: {str(e)}")
        
        return errors
    
    def _validate_security(self, code: str) -> List[str]:
        """Validate security and detect dangerous patterns"""
        security_issues = []
        
        # Check for dangerous imports
        for dangerous_import in self.dangerous_imports:
            patterns = [
                rf'import\s+{dangerous_import}(?:\s|$)',
                rf'from\s+{dangerous_import}\s+import',
                rf'__import__\s*\(\s*[\'\"]{dangerous_import}[\'\"]'
            ]
            
            for pattern in patterns:
                if re.search(pattern, code, re.IGNORECASE):
                    security_issues.append(f"Dangerous import detected: {dangerous_import}")
        
        # Check for dangerous functions
        for dangerous_func in self.dangerous_functions:
            pattern = rf'{dangerous_func}\s*\('
            if re.search(pattern, code, re.IGNORECASE):
                security_issues.append(f"Dangerous function detected: {dangerous_func}")
        
        # Check for file operations
        file_patterns = [
            r'open\s*\(',
            r'file\s*\(',
            r'\.read\s*\(',
            r'\.write\s*\(',
            r'\.close\s*\('
        ]
        
        for pattern in file_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                security_issues.append("File operation detected - not allowed in strategies")
        
        # Check for network operations
        network_patterns = [
            r'urllib',
            r'requests\.',
            r'socket\.',
            r'http\.',
            r'ftp\.'
        ]
        
        for pattern in network_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                security_issues.append("Network operation detected - not allowed in strategies")
        
        return security_issues
    
    def _validate_structure(self, code: str) -> Tuple[List[str], List[str]]:
        """Validate strategy structure and required components"""
        errors = []
        warnings = []
        
        # Check for strategy class
        if not re.search(r'class\s+\w+\s*\(\s*bt\.Strategy\s*\)', code):
            errors.append("No valid Strategy class inheriting from bt.Strategy found")
        
        # Check for required methods
        for method in self.required_methods:
            if f'def {method}' not in code:
                errors.append(f"Required method '{method}' not found")
        
        # Check for recommended methods
        for method in self.recommended_methods:
            if f'def {method}' not in code:
                warnings.append(f"Recommended method '{method}' not found")
        
        # Check for proper initialization
        if '__init__' in code:
            if 'super().__init__()' not in code and 'super(' not in code:
                warnings.append("Strategy __init__ should call super().__init__()")
        
        # Check for data access patterns
        if 'self.data' not in code and 'self.datas' not in code:
            warnings.append("Strategy doesn't seem to access data feeds")
        
        return errors, warnings
    
    def _validate_risk_management(self, code: str) -> List[str]:
        """Validate risk management components"""
        warnings = []
        
        # Check for stop loss
        stop_loss_patterns = [
            r'stop.?loss',
            r'sl\s*=',
            r'\.close\s*\(',
            r'self\.sell\s*\(',
            r'self\.buy\s*\('
        ]
        
        has_stop_loss = any(re.search(pattern, code, re.IGNORECASE) for pattern in stop_loss_patterns)
        if not has_stop_loss:
            warnings.append("No stop loss mechanism detected - consider adding risk management")
        
        # Check for position sizing
        position_patterns = [
            r'size\s*=',
            r'\.size',
            r'position.?siz',
            r'cash\s*\*',
            r'broker\.getcash'
        ]
        
        has_position_sizing = any(re.search(pattern, code, re.IGNORECASE) for pattern in position_patterns)
        if not has_position_sizing:
            warnings.append("No position sizing logic detected - consider adding position management")
        
        # Check for portfolio limits
        limit_patterns = [
            r'max.?position',
            r'portfolio.?limit',
            r'exposure.?limit'
        ]
        
        has_limits = any(re.search(pattern, code, re.IGNORECASE) for pattern in limit_patterns)
        if not has_limits:
            warnings.append("No portfolio limits detected - consider adding exposure controls")
        
        return warnings
    
    def _validate_performance(self, code: str) -> List[str]:
        """Validate performance considerations"""
        warnings = []
        
        # Check for excessive loops
        loop_count = len(re.findall(r'for\s+\w+\s+in', code))
        if loop_count > 5:
            warnings.append(f"High number of loops ({loop_count}) detected - may impact performance")
        
        # Check for nested loops
        if re.search(r'for\s+\w+\s+in.*?for\s+\w+\s+in', code, re.DOTALL):
            warnings.append("Nested loops detected - may impact performance")
        
        # Check for complex calculations in next()
        if 'def next' in code:
            next_method = self._extract_method(code, 'next')
            if next_method:
                calc_patterns = [
                    r'\.rolling\s*\(',
                    r'\.ewm\s*\(',
                    r'\.resample\s*\(',
                    r'pd\.',
                    r'np\.'
                ]
                
                complex_calcs = sum(1 for pattern in calc_patterns if re.search(pattern, next_method))
                if complex_calcs > 3:
                    warnings.append("Complex calculations in next() method - consider moving to __init__")
        
        return warnings
    
    def _generate_recommendations(self, code: str) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        # Logging recommendations
        if 'self.log(' not in code:
            recommendations.append("Add logging with self.log() for better debugging")
        
        # Documentation recommendations
        if '"""' not in code and "'''" not in code:
            recommendations.append("Add docstrings to document strategy logic")
        
        # Error handling recommendations
        if 'try:' not in code:
            recommendations.append("Add error handling with try/except blocks")
        
        # Parameter recommendations
        if 'self.params' not in code and 'self.p.' not in code:
            recommendations.append("Consider using strategy parameters for flexibility")
        
        # Indicator recommendations
        if 'bt.indicators' not in code and 'bt.ind' not in code:
            recommendations.append("Consider using Backtrader built-in indicators")
        
        return recommendations
    
    def _calculate_code_metrics(self, code: str) -> Dict[str, Any]:
        """Calculate code quality metrics"""
        
        lines = code.split('\n')
        
        metrics = {
            'total_lines': len(lines),
            'code_lines': len([line for line in lines if line.strip() and not line.strip().startswith('#')]),
            'comment_lines': len([line for line in lines if line.strip().startswith('#')]),
            'blank_lines': len([line for line in lines if not line.strip()]),
            'methods_count': len(re.findall(r'def\s+\w+', code)),
            'classes_count': len(re.findall(r'class\s+\w+', code)),
            'complexity_score': self._calculate_complexity(code)
        }
        
        # Calculate comment ratio
        if metrics['code_lines'] > 0:
            metrics['comment_ratio'] = metrics['comment_lines'] / metrics['code_lines']
        else:
            metrics['comment_ratio'] = 0
        
        return metrics
    
    def _calculate_complexity(self, code: str) -> int:
        """Calculate cyclomatic complexity approximation"""
        
        complexity_keywords = [
            'if', 'elif', 'else', 'for', 'while', 'try', 'except', 
            'finally', 'with', 'and', 'or', 'break', 'continue'
        ]
        
        complexity = 1  # Base complexity
        
        for keyword in complexity_keywords:
            pattern = rf'\b{keyword}\b'
            complexity += len(re.findall(pattern, code))
        
        return complexity
    
    def _extract_method(self, code: str, method_name: str) -> str:
        """Extract specific method from code"""
        
        pattern = rf'def\s+{method_name}\s*\([^)]*\):(.*?)(?=def\s+\w+|class\s+\w+|$)'
        match = re.search(pattern, code, re.DOTALL)
        
        if match:
            return match.group(1)
        
        return ""
    
    def sanitize_code(self, code: str) -> str:
        """Sanitize code by removing dangerous patterns"""
        
        # Remove dangerous imports
        for dangerous_import in self.dangerous_imports:
            patterns = [
                rf'import\s+{dangerous_import}(?:\s|$).*?\n',
                rf'from\s+{dangerous_import}\s+import.*?\n'
            ]
            
            for pattern in patterns:
                code = re.sub(pattern, '', code, flags=re.IGNORECASE | re.MULTILINE)
        
        # Remove dangerous function calls
        for dangerous_func in self.dangerous_functions:
            pattern = rf'{dangerous_func}\s*\([^)]*\)'
            code = re.sub(pattern, f'# {dangerous_func} removed for security', code, flags=re.IGNORECASE)
        
        return code
    
    def get_validation_summary(self, validation_result: Dict[str, Any]) -> str:
        """Generate human-readable validation summary"""
        
        summary = []
        
        if validation_result['is_valid']:
            summary.append("✅ Strategy validation passed")
        else:
            summary.append("❌ Strategy validation failed")
        
        if validation_result['errors']:
            summary.append(f"\n🚨 Errors ({len(validation_result['errors'])}):")
            for error in validation_result['errors']:
                summary.append(f"  • {error}")
        
        if validation_result['security_issues']:
            summary.append(f"\n🔒 Security Issues ({len(validation_result['security_issues'])}):")
            for issue in validation_result['security_issues']:
                summary.append(f"  • {issue}")
        
        if validation_result['warnings']:
            summary.append(f"\n⚠️ Warnings ({len(validation_result['warnings'])}):")
            for warning in validation_result['warnings'][:5]:  # Limit to 5 warnings
                summary.append(f"  • {warning}")
        
        if validation_result['recommendations']:
            summary.append(f"\n💡 Recommendations ({len(validation_result['recommendations'])}):")
            for rec in validation_result['recommendations'][:3]:  # Limit to 3 recommendations
                summary.append(f"  • {rec}")
        
        # Add metrics summary
        metrics = validation_result['metrics']
        if metrics:
            summary.append(f"\n📊 Code Metrics:")
            summary.append(f"  • Lines of code: {metrics.get('code_lines', 0)}")
            summary.append(f"  • Methods: {metrics.get('methods_count', 0)}")
            summary.append(f"  • Complexity: {metrics.get('complexity_score', 0)}")
            summary.append(f"  • Comment ratio: {metrics.get('comment_ratio', 0):.1%}")
        
        return '\n'.join(summary)
