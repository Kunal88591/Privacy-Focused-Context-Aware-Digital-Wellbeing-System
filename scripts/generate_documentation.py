#!/usr/bin/env python3
"""
Comprehensive Project Documentation Generator

This script scans the entire codebase and generates detailed documentation
for every file, function, class, and component in the project.
"""

import os
import ast
import json
import re
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class CodeAnalyzer:
    """Analyzes Python and JavaScript code to extract structure and documentation"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.documentation = {
            "project_name": "Privacy-Focused Context-Aware Digital Wellbeing System",
            "version": "1.0.0",
            "generation_date": datetime.now().isoformat(),
            "statistics": {},
            "backend": {},
            "mobile": {},
            "ai_models": {},
            "iot": {},
            "tests": {},
            "configs": {}
        }
    
    def analyze_python_file(self, filepath: Path) -> Dict[str, Any]:
        """Analyze a Python file and extract all functions, classes, and docstrings"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            file_info = {
                "path": str(filepath.relative_to(self.project_root)),
                "type": "python",
                "lines": len(content.splitlines()),
                "docstring": ast.get_docstring(tree) or "",
                "imports": [],
                "classes": [],
                "functions": [],
                "constants": [],
                "decorators": []
            }
            
            # Extract imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        file_info["imports"].append({
                            "name": alias.name,
                            "alias": alias.asname
                        })
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        file_info["imports"].append({
                            "from": module,
                            "name": alias.name,
                            "alias": alias.asname
                        })
            
            # Extract classes
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = {
                        "name": node.name,
                        "lineno": node.lineno,
                        "docstring": ast.get_docstring(node) or "",
                        "bases": [self._get_name(base) for base in node.bases],
                        "decorators": [self._get_name(dec) for dec in node.decorator_list],
                        "methods": []
                    }
                    
                    # Extract methods
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method_info = self._analyze_function(item)
                            class_info["methods"].append(method_info)
                    
                    file_info["classes"].append(class_info)
                
                # Extract top-level functions
                elif isinstance(node, ast.FunctionDef):
                    func_info = self._analyze_function(node)
                    file_info["functions"].append(func_info)
                
                # Extract constants
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id.isupper():
                            file_info["constants"].append({
                                "name": target.id,
                                "lineno": node.lineno
                            })
            
            return file_info
            
        except Exception as e:
            return {
                "path": str(filepath.relative_to(self.project_root)),
                "error": str(e),
                "type": "python"
            }
    
    def _analyze_function(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """Analyze a function node"""
        func_info = {
            "name": node.name,
            "lineno": node.lineno,
            "docstring": ast.get_docstring(node) or "",
            "decorators": [self._get_name(dec) for dec in node.decorator_list],
            "parameters": [],
            "returns": None,
            "is_async": isinstance(node, ast.AsyncFunctionDef)
        }
        
        # Extract parameters
        for arg in node.args.args:
            param = {"name": arg.arg}
            if arg.annotation:
                param["type"] = self._get_name(arg.annotation)
            func_info["parameters"].append(param)
        
        # Extract return type
        if node.returns:
            func_info["returns"] = self._get_name(node.returns)
        
        return func_info
    
    def _get_name(self, node) -> str:
        """Get name from AST node"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Subscript):
            return f"{self._get_name(node.value)}[{self._get_name(node.slice)}]"
        elif isinstance(node, ast.Constant):
            return str(node.value)
        return ast.unparse(node) if hasattr(ast, 'unparse') else str(node)
    
    def analyze_javascript_file(self, filepath: Path) -> Dict[str, Any]:
        """Analyze a JavaScript/JSX file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_info = {
                "path": str(filepath.relative_to(self.project_root)),
                "type": "javascript",
                "lines": len(content.splitlines()),
                "imports": [],
                "exports": [],
                "components": [],
                "functions": [],
                "hooks": []
            }
            
            # Extract imports
            import_pattern = r'import\s+(?:{([^}]+)}|(\w+))\s+from\s+[\'"]([^\'"]+)[\'"]'
            for match in re.finditer(import_pattern, content):
                if match.group(1):  # Named imports
                    imports = [i.strip() for i in match.group(1).split(',')]
                    file_info["imports"].append({
                        "type": "named",
                        "names": imports,
                        "from": match.group(3)
                    })
                elif match.group(2):  # Default import
                    file_info["imports"].append({
                        "type": "default",
                        "name": match.group(2),
                        "from": match.group(3)
                    })
            
            # Extract React components
            component_pattern = r'(?:export\s+)?(?:const|function)\s+(\w+)\s*=?\s*\(([^)]*)\)\s*(?:=>|{)'
            for match in re.finditer(component_pattern, content):
                name = match.group(1)
                if name[0].isupper():  # React components start with uppercase
                    file_info["components"].append({
                        "name": name,
                        "props": match.group(2).strip()
                    })
            
            # Extract hooks
            hook_pattern = r'const\s+\[(\w+),\s*set\w+\]\s*=\s*useState'
            for match in re.finditer(hook_pattern, content):
                file_info["hooks"].append({
                    "type": "useState",
                    "state": match.group(1)
                })
            
            # Extract useEffect
            if 'useEffect' in content:
                effect_count = content.count('useEffect(')
                file_info["hooks"].append({
                    "type": "useEffect",
                    "count": effect_count
                })
            
            # Extract exports
            export_pattern = r'export\s+(?:default\s+)?(?:const|function|class)?\s+(\w+)'
            for match in re.finditer(export_pattern, content):
                file_info["exports"].append(match.group(1))
            
            return file_info
            
        except Exception as e:
            return {
                "path": str(filepath.relative_to(self.project_root)),
                "error": str(e),
                "type": "javascript"
            }
    
    def analyze_json_file(self, filepath: Path) -> Dict[str, Any]:
        """Analyze a JSON configuration file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = json.load(f)
            
            return {
                "path": str(filepath.relative_to(self.project_root)),
                "type": "json",
                "keys": list(content.keys()) if isinstance(content, dict) else [],
                "structure": self._get_json_structure(content)
            }
        except Exception as e:
            return {
                "path": str(filepath.relative_to(self.project_root)),
                "error": str(e),
                "type": "json"
            }
    
    def _get_json_structure(self, data, depth=0, max_depth=3) -> Any:
        """Get simplified structure of JSON data"""
        if depth > max_depth:
            return "..."
        
        if isinstance(data, dict):
            return {k: self._get_json_structure(v, depth+1, max_depth) for k, v in list(data.items())[:10]}
        elif isinstance(data, list):
            if len(data) > 0:
                return [self._get_json_structure(data[0], depth+1, max_depth)]
            return []
        else:
            return type(data).__name__
    
    def scan_project(self):
        """Scan the entire project and analyze all files"""
        print("🔍 Scanning project files...")
        
        # Define file patterns
        patterns = {
            'python': ['**/*.py'],
            'javascript': ['**/*.js', '**/*.jsx'],
            'json': ['**/*.json'],
            'yaml': ['**/*.yml', '**/*.yaml']
        }
        
        # Exclude patterns
        exclude_dirs = {'node_modules', '__pycache__', '.git', 'build', 'dist', '.pytest_cache'}
        
        stats = {
            'total_files': 0,
            'total_lines': 0,
            'by_type': {},
            'by_category': {}
        }
        
        for file_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                for filepath in self.project_root.glob(pattern):
                    # Skip excluded directories
                    if any(excluded in filepath.parts for excluded in exclude_dirs):
                        continue
                    
                    print(f"  Analyzing: {filepath.relative_to(self.project_root)}")
                    
                    # Analyze based on file type
                    if file_type == 'python':
                        file_data = self.analyze_python_file(filepath)
                    elif file_type == 'javascript':
                        file_data = self.analyze_javascript_file(filepath)
                    elif file_type == 'json':
                        file_data = self.analyze_json_file(filepath)
                    else:
                        continue
                    
                    # Categorize file
                    rel_path = filepath.relative_to(self.project_root)
                    category = self._categorize_file(rel_path)
                    
                    if category not in self.documentation:
                        self.documentation[category] = {}
                    
                    self.documentation[category][str(rel_path)] = file_data
                    
                    # Update statistics
                    stats['total_files'] += 1
                    if 'lines' in file_data:
                        stats['total_lines'] += file_data['lines']
                    
                    stats['by_type'][file_type] = stats['by_type'].get(file_type, 0) + 1
                    stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
        
        self.documentation['statistics'] = stats
        print(f"\n✅ Analyzed {stats['total_files']} files ({stats['total_lines']:,} lines)")
    
    def _categorize_file(self, filepath: Path) -> str:
        """Categorize file based on path"""
        parts = filepath.parts
        
        if 'backend-api' in parts:
            if 'tests' in parts:
                return 'backend_tests'
            return 'backend'
        elif 'mobile-app' in parts:
            if '__tests__' in parts or 'tests' in parts:
                return 'mobile_tests'
            return 'mobile'
        elif 'ai-models' in parts:
            if 'tests' in parts:
                return 'ai_tests'
            return 'ai_models'
        elif 'iot-device' in parts:
            return 'iot'
        else:
            return 'configs'
    
    def generate_markdown_documentation(self) -> str:
        """Generate comprehensive markdown documentation"""
        md = []
        
        # Title and metadata
        md.append(f"# {self.documentation['project_name']} - Complete Code Documentation\n")
        md.append(f"**Version:** {self.documentation['version']}  ")
        md.append(f"**Generated:** {self.documentation['generation_date']}  ")
        md.append(f"**Total Files:** {self.documentation['statistics']['total_files']}  ")
        md.append(f"**Total Lines:** {self.documentation['statistics']['total_lines']:,}\n")
        
        # Table of contents
        md.append("## 📑 Table of Contents\n")
        md.append("1. [Project Overview](#project-overview)")
        md.append("2. [Statistics](#statistics)")
        md.append("3. [Backend API](#backend-api)")
        md.append("4. [Mobile Application](#mobile-application)")
        md.append("5. [AI/ML Models](#aiml-models)")
        md.append("6. [IoT Device](#iot-device)")
        md.append("7. [Tests](#tests)")
        md.append("8. [Configuration Files](#configuration-files)\n")
        
        # Project overview
        md.append("## Project Overview\n")
        md.append("Privacy-Focused Context-Aware Digital Wellbeing System is a comprehensive solution ")
        md.append("that combines backend API, mobile application, AI/ML models, and IoT integration ")
        md.append("to provide intelligent notification management, focus mode, privacy protection, ")
        md.append("and wellness monitoring.\n")
        
        # Statistics
        md.append("## Statistics\n")
        stats = self.documentation['statistics']
        md.append(f"- **Total Files Analyzed:** {stats['total_files']}")
        md.append(f"- **Total Lines of Code:** {stats['total_lines']:,}")
        md.append("\n### Files by Type\n")
        for file_type, count in stats['by_type'].items():
            md.append(f"- **{file_type.capitalize()}:** {count} files")
        md.append("\n### Files by Category\n")
        for category, count in stats['by_category'].items():
            md.append(f"- **{category.replace('_', ' ').title()}:** {count} files")
        md.append("")
        
        # Backend API documentation
        md.append("## Backend API\n")
        md.append("The backend API is built with FastAPI and provides RESTful endpoints for all system functionality.\n")
        
        if 'backend' in self.documentation:
            backend_files = self.documentation['backend']
            
            # Group files by subdirectory
            api_files = {k: v for k, v in backend_files.items() if '/api/' in k}
            service_files = {k: v for k, v in backend_files.items() if '/services/' in k}
            core_files = {k: v for k, v in backend_files.items() if '/core/' in k}
            
            if api_files:
                md.append("### API Endpoints\n")
                for filepath, data in sorted(api_files.items()):
                    md.extend(self._document_python_file(filepath, data))
            
            if service_files:
                md.append("### Services\n")
                for filepath, data in sorted(service_files.items()):
                    md.extend(self._document_python_file(filepath, data))
            
            if core_files:
                md.append("### Core Modules\n")
                for filepath, data in sorted(core_files.items()):
                    md.extend(self._document_python_file(filepath, data))
        
        # Mobile application documentation
        md.append("## Mobile Application\n")
        md.append("React Native mobile application for Android with offline-first architecture.\n")
        
        if 'mobile' in self.documentation:
            mobile_files = self.documentation['mobile']
            
            screen_files = {k: v for k, v in mobile_files.items() if '/screens/' in k}
            service_files = {k: v for k, v in mobile_files.items() if '/services/' in k}
            component_files = {k: v for k, v in mobile_files.items() if '/components/' in k}
            
            if screen_files:
                md.append("### Screens\n")
                for filepath, data in sorted(screen_files.items()):
                    md.extend(self._document_javascript_file(filepath, data))
            
            if component_files:
                md.append("### Components\n")
                for filepath, data in sorted(component_files.items()):
                    md.extend(self._document_javascript_file(filepath, data))
            
            if service_files:
                md.append("### Services\n")
                for filepath, data in sorted(service_files.items()):
                    md.extend(self._document_javascript_file(filepath, data))
        
        # AI/ML models documentation
        md.append("## AI/ML Models\n")
        md.append("TensorFlow-based machine learning models for intelligent classification and prediction.\n")
        
        if 'ai_models' in self.documentation:
            for filepath, data in sorted(self.documentation['ai_models'].items()):
                md.extend(self._document_python_file(filepath, data))
        
        # IoT device documentation
        md.append("## IoT Device\n")
        md.append("Raspberry Pi-based IoT device with environmental sensors.\n")
        
        if 'iot' in self.documentation:
            for filepath, data in sorted(self.documentation['iot'].items()):
                md.extend(self._document_python_file(filepath, data))
        
        # Tests documentation
        md.append("## Tests\n")
        md.append("Comprehensive test suite covering backend, mobile, and AI components.\n")
        
        test_count = 0
        if 'backend_tests' in self.documentation:
            test_count += len(self.documentation['backend_tests'])
        if 'mobile_tests' in self.documentation:
            test_count += len(self.documentation['mobile_tests'])
        
        md.append(f"**Total Test Files:** {test_count}\n")
        
        # Configuration files
        md.append("## Configuration Files\n")
        if 'configs' in self.documentation:
            for filepath, data in sorted(self.documentation['configs'].items()):
                md.append(f"### {filepath}\n")
                if 'keys' in data:
                    md.append(f"**Configuration Keys:** {', '.join(data['keys'][:10])}\n")
        
        return '\n'.join(md)
    
    def _document_python_file(self, filepath: str, data: Dict[str, Any]) -> List[str]:
        """Generate documentation for a Python file"""
        lines = []
        
        lines.append(f"#### {filepath}\n")
        lines.append(f"**Lines:** {data.get('lines', 'N/A')}  ")
        lines.append(f"**Type:** Python Module\n")
        
        if data.get('docstring'):
            lines.append(f"**Description:** {data['docstring'][:200]}...\n")
        
        # Document classes
        if data.get('classes'):
            lines.append("**Classes:**\n")
            for cls in data['classes']:
                lines.append(f"- `{cls['name']}` (line {cls['lineno']})")
                if cls.get('docstring'):
                    lines.append(f"  - {cls['docstring'][:100]}")
                if cls.get('methods'):
                    lines.append(f"  - Methods: {len(cls['methods'])}")
                    for method in cls['methods'][:5]:  # Show first 5 methods
                        params = ', '.join([p['name'] for p in method.get('parameters', [])])
                        lines.append(f"    - `{method['name']}({params})`")
        
        # Document functions
        if data.get('functions'):
            lines.append("**Functions:**\n")
            for func in data['functions'][:10]:  # Show first 10 functions
                params = ', '.join([p['name'] for p in func.get('parameters', [])])
                lines.append(f"- `{func['name']}({params})` (line {func['lineno']})")
                if func.get('docstring'):
                    lines.append(f"  - {func['docstring'][:100]}")
        
        # Document imports
        if data.get('imports') and len(data['imports']) > 0:
            lines.append(f"**Key Imports:** {len(data['imports'])} modules\n")
        
        lines.append("")
        return lines
    
    def _document_javascript_file(self, filepath: str, data: Dict[str, Any]) -> List[str]:
        """Generate documentation for a JavaScript file"""
        lines = []
        
        lines.append(f"#### {filepath}\n")
        lines.append(f"**Lines:** {data.get('lines', 'N/A')}  ")
        lines.append(f"**Type:** JavaScript/React\n")
        
        # Document React components
        if data.get('components'):
            lines.append("**React Components:**\n")
            for comp in data['components']:
                lines.append(f"- `{comp['name']}` - Props: {comp.get('props', 'none')}")
        
        # Document hooks
        if data.get('hooks'):
            lines.append("**React Hooks:**\n")
            for hook in data['hooks'][:10]:
                if hook['type'] == 'useState':
                    lines.append(f"- useState: `{hook['state']}`")
                elif hook['type'] == 'useEffect':
                    lines.append(f"- useEffect: {hook['count']} effects")
        
        # Document imports
        if data.get('imports') and len(data['imports']) > 0:
            lines.append(f"**Imports:** {len(data['imports'])} modules\n")
        
        lines.append("")
        return lines
    
    def save_documentation(self, output_file: str):
        """Save documentation to file"""
        markdown_doc = self.generate_markdown_documentation()
        
        output_path = self.project_root / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_doc)
        
        print(f"\n📄 Documentation saved to: {output_path}")
        print(f"📊 Documentation size: {len(markdown_doc):,} characters")
        
        return output_path


def main():
    """Main execution function"""
    print("=" * 70)
    print("  COMPREHENSIVE PROJECT DOCUMENTATION GENERATOR")
    print("  Privacy-Focused Context-Aware Digital Wellbeing System")
    print("=" * 70)
    print()
    
    # Get project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    print(f"📁 Project Root: {project_root}")
    print()
    
    # Create analyzer
    analyzer = CodeAnalyzer(str(project_root))
    
    # Scan project
    analyzer.scan_project()
    
    # Generate documentation
    print("\n📝 Generating comprehensive documentation...")
    output_file = analyzer.save_documentation("COMPLETE_CODE_DOCUMENTATION.md")
    
    print("\n✅ Documentation generation complete!")
    print(f"\n📖 View documentation: {output_file}")
    print("\n💡 To convert to PDF, use:")
    print("   pandoc COMPLETE_CODE_DOCUMENTATION.md -o COMPLETE_CODE_DOCUMENTATION.pdf")
    

if __name__ == "__main__":
    main()
