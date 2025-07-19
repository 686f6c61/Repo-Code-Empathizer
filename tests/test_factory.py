"""Tests for analyzer factory"""
import pytest
from src.language_analyzers.factory import AnalyzerFactory
from src.language_analyzers.base import LanguageAnalyzer
from src.language_analyzers.python_analyzer import PythonAnalyzer
from src.language_analyzers.javascript_analyzer import JavaScriptAnalyzer
from src.language_analyzers.typescript_analyzer import TypeScriptAnalyzer
from src.language_analyzers.java_analyzer import JavaAnalyzer


class TestAnalyzerFactory:
    
    def test_get_analyzer(self):
        python_analyzer = AnalyzerFactory.get_analyzer('python')
        assert isinstance(python_analyzer, PythonAnalyzer)
        
        js_analyzer = AnalyzerFactory.get_analyzer('javascript')
        assert isinstance(js_analyzer, JavaScriptAnalyzer)
        
        ts_analyzer = AnalyzerFactory.get_analyzer('typescript')
        assert isinstance(ts_analyzer, TypeScriptAnalyzer)
        
        java_analyzer = AnalyzerFactory.get_analyzer('java')
        assert isinstance(java_analyzer, JavaAnalyzer)
        
        # Test case insensitive
        assert isinstance(AnalyzerFactory.get_analyzer('PYTHON'), PythonAnalyzer)
        
        # Test unknown language
        assert AnalyzerFactory.get_analyzer('unknown') is None
    
    def test_get_analyzer_for_file(self):
        assert isinstance(AnalyzerFactory.get_analyzer_for_file('test.py'), PythonAnalyzer)
        assert isinstance(AnalyzerFactory.get_analyzer_for_file('test.js'), JavaScriptAnalyzer)
        assert isinstance(AnalyzerFactory.get_analyzer_for_file('test.jsx'), JavaScriptAnalyzer)
        assert isinstance(AnalyzerFactory.get_analyzer_for_file('test.ts'), TypeScriptAnalyzer)
        assert isinstance(AnalyzerFactory.get_analyzer_for_file('test.tsx'), TypeScriptAnalyzer)
        assert isinstance(AnalyzerFactory.get_analyzer_for_file('Test.java'), JavaAnalyzer)
        
        # Test unknown extension
        assert AnalyzerFactory.get_analyzer_for_file('test.unknown') is None
    
    def test_get_supported_extensions(self):
        extensions = AnalyzerFactory.get_supported_extensions()
        assert '.py' in extensions
        assert '.js' in extensions
        assert '.ts' in extensions
        assert '.java' in extensions
        assert len(extensions) >= 7  # py, js, jsx, mjs, ts, tsx, java
    
    def test_get_supported_languages(self):
        languages = AnalyzerFactory.get_supported_languages()
        assert 'python' in languages
        assert 'javascript' in languages
        assert 'typescript' in languages
        assert 'java' in languages
        assert len(languages) == 4
    
    def test_detect_primary_language(self):
        files = {
            'main.py': 'content',
            'utils.py': 'content',
            'test.py': 'content',
            'config.js': 'content',
            'README.md': 'content'
        }
        
        primary = AnalyzerFactory.detect_primary_language(files)
        assert primary == 'python'  # 3 Python files vs 1 JavaScript
        
        # Test with more JavaScript files
        files2 = {
            'index.js': 'content',
            'app.js': 'content',
            'utils.js': 'content',
            'test.py': 'content'
        }
        
        primary2 = AnalyzerFactory.detect_primary_language(files2)
        assert primary2 == 'javascript'
        
        # Test with no recognized files
        files3 = {
            'README.md': 'content',
            'config.yml': 'content'
        }
        
        primary3 = AnalyzerFactory.detect_primary_language(files3)
        assert primary3 is None
    
    def test_register_analyzer(self):
        # Create a mock analyzer
        class MockAnalyzer(LanguageAnalyzer):
            def get_file_extensions(self):
                return ['.mock']
            
            def get_language_name(self):
                return 'Mock'
            
            def analyze_file(self, file_path, content):
                return {}
        
        # Register the analyzer
        AnalyzerFactory.register_analyzer('mock', MockAnalyzer)
        
        # Test that it's registered
        analyzer = AnalyzerFactory.get_analyzer('mock')
        assert isinstance(analyzer, MockAnalyzer)
        assert 'mock' in AnalyzerFactory.get_supported_languages()
    
    def test_analyze_multi_language_project(self):
        files = {
            'backend/main.py': 'def main():\n    pass',
            'backend/utils.py': 'def util():\n    pass',
            'frontend/app.js': 'function app() {\n    console.log("app");\n}',
            'frontend/utils.ts': 'function util(): void {\n    console.log("util");\n}',
            'Main.java': 'public class Main {\n    public static void main(String[] args) {}\n}'
        }
        
        results = AnalyzerFactory.analyze_multi_language_project(files)
        
        # Check structure
        assert 'languages' in results
        assert 'total_metrics' in results
        assert 'primary_language' in results
        
        # Check languages detected
        assert 'Python' in results['languages']
        assert 'JavaScript' in results['languages']
        assert 'TypeScript' in results['languages']
        assert 'Java' in results['languages']
        
        # Check file counts
        assert results['languages']['Python']['file_count'] == 2
        assert results['languages']['JavaScript']['file_count'] == 1
        assert results['languages']['TypeScript']['file_count'] == 1
        assert results['languages']['Java']['file_count'] == 1
        
        # Check primary language (Python has most files)
        assert results['primary_language'] == 'Python'
        
        # Check total metrics
        assert results['total_metrics']['total_files'] == 5
        assert results['total_metrics']['languages_analyzed'] == ['Python', 'JavaScript', 'TypeScript', 'Java']
        assert 'overall_empathy_score' in results['total_metrics']