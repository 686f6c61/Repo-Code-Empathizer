"""
Integration tests for console functionality
Verifies the CLI works without errors in different scenarios
"""

import os
import sys
import subprocess
import tempfile
import json
from pathlib import Path
import pytest

# Get paths
PROJECT_ROOT = Path(__file__).parent.parent
SRC_PATH = PROJECT_ROOT / "src"
MAIN_SCRIPT = SRC_PATH / "main.py"


class TestConsoleIntegration:
    """Test the complete console application"""
    
    @pytest.fixture
    def env_with_token(self):
        """Provide environment with GitHub token"""
        env = os.environ.copy()
        # Use a dummy token for testing (won't make real API calls)
        if 'GITHUB_TOKEN' not in env:
            env['GITHUB_TOKEN'] = 'dummy_token_for_testing'
        return env
    
    def run_command(self, args, env=None):
        """Run the main.py script with given arguments"""
        cmd = [sys.executable, str(MAIN_SCRIPT)] + args
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env or os.environ.copy(),
            cwd=str(PROJECT_ROOT)
        )
        
        return result
    
    def test_help_command(self):
        """Test that help command works"""
        result = self.run_command(['--help'])
        
        assert result.returncode == 0
        assert 'Repo Code Empathizer' in result.stdout
        assert '--empresa' in result.stdout
        assert '--candidato' in result.stdout
        assert '--output' in result.stdout
    
    def test_list_languages_command(self):
        """Test listing supported languages"""
        result = self.run_command(['--list-languages'])
        
        assert result.returncode == 0
        assert 'Lenguajes Soportados' in result.stdout
        assert 'python' in result.stdout.lower()
        assert 'javascript' in result.stdout.lower()
        assert 'java' in result.stdout.lower()
    
    def test_missing_token_error(self):
        """Test error when GitHub token is missing"""
        env = os.environ.copy()
        env.pop('GITHUB_TOKEN', None)
        
        # Create a temporary .env file without token
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', dir=PROJECT_ROOT, delete=False) as f:
            f.write("# No token\n")
            temp_env_file = f.name
        
        try:
            result = self.run_command(
                ['--empresa', 'test/repo1', '--candidato', 'test/repo2'],
                env=env
            )
            
            # Should fail due to missing token
            assert result.returncode != 0 or 'Token' in result.stderr or 'Token' in result.stdout
        finally:
            os.unlink(temp_env_file)
    
    @pytest.mark.parametrize("output_format", ['txt', 'json', 'html', 'dashboard', 'all'])
    def test_output_formats(self, output_format):
        """Test different output format options"""
        result = self.run_command(['--help'])
        
        # Help should show all output formats
        assert output_format in result.stdout
    
    def test_invalid_arguments(self):
        """Test handling of invalid arguments"""
        result = self.run_command(['--invalid-option'])
        
        assert result.returncode != 0
        assert 'error' in result.stderr.lower() or 'invalid' in result.stderr.lower()
    
    def test_config_file_option(self):
        """Test custom config file option"""
        # Create temporary config
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("""
analysis:
  max_files_per_language: 50
weights:
  nombres: 0.20
  documentacion: 0.20
""")
            config_file = f.name
        
        try:
            result = self.run_command(['--config', config_file, '--help'])
            assert result.returncode == 0
        finally:
            os.unlink(config_file)
    
    def test_repo_url_formats(self):
        """Test different repository URL formats are accepted"""
        test_cases = [
            ('user/repo', True),
            ('https://github.com/user/repo', True),
            ('http://github.com/user/repo', True),
            ('github.com/user/repo', True),
            ('invalid-format', False),
            ('', False)
        ]
        
        # Import the URL extraction function
        sys.path.insert(0, str(SRC_PATH))
        from github_utils import GitHubRepo
        
        for url, should_work in test_cases:
            if should_work:
                try:
                    result = GitHubRepo.extraer_usuario_repo(url)
                    assert '/' in result
                except:
                    pytest.fail(f"Failed to parse valid URL: {url}")
            else:
                with pytest.raises(ValueError):
                    GitHubRepo.extraer_usuario_repo(url)
    
    def test_parallel_and_cache_options(self):
        """Test parallel processing and cache options"""
        # Test no-cache option
        result = self.run_command(['--help'])
        assert '--no-cache' in result.stdout
        assert '--clear-cache' in result.stdout
        assert '--parallel' in result.stdout
    
    def test_import_all_modules(self):
        """Test that all modules can be imported without errors"""
        modules_to_test = [
            'github_utils',
            'language_analyzers.factory',
            'language_analyzers.python_analyzer',
            'language_analyzers.javascript_analyzer',
            'language_analyzers.typescript_analyzer',
            'language_analyzers.java_analyzer',
            'language_analyzers.go_analyzer',
            'language_analyzers.csharp_analyzer',
            'language_analyzers.cpp_analyzer',
            'language_analyzers.php_analyzer',
            'language_analyzers.ruby_analyzer',
            'language_analyzers.swift_analyzer',
            'language_analyzers.html_analyzer',
            'language_analyzers.css_analyzer',
            'exporters',
            'parallel_analyzer',
            'cache_manager',
            'empathy_algorithm'
        ]
        
        sys.path.insert(0, str(SRC_PATH))
        
        for module in modules_to_test:
            try:
                __import__(module)
            except ImportError as e:
                pytest.fail(f"Failed to import {module}: {e}")
    
    def test_color_output(self):
        """Test that color codes are properly defined"""
        sys.path.insert(0, str(SRC_PATH))
        from main import COLORS
        
        required_colors = ['header', 'blue', 'cyan', 'green', 'warning', 'fail', 'end', 'bold']
        for color in required_colors:
            assert color in COLORS
            assert isinstance(COLORS[color], str)
            assert COLORS[color].startswith('\033[')


class TestMainFunctions:
    """Test individual functions from main.py"""
    
    def test_load_config(self):
        """Test config loading function"""
        sys.path.insert(0, str(SRC_PATH))
        from main import load_config
        
        # Test with non-existent file
        config = load_config('non_existent.yaml')
        assert config == {}
        
        # Test with valid YAML
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("test: value\nnumber: 42")
            temp_file = f.name
        
        try:
            config = load_config(temp_file)
            assert config['test'] == 'value'
            assert config['number'] == 42
        finally:
            os.unlink(temp_file)
    
    def test_mostrar_resumen_function(self):
        """Test the summary display function"""
        sys.path.insert(0, str(SRC_PATH))
        from main import mostrar_resumen
        
        # Test with sample data
        test_results = {
            'repos': {
                'empresa': {
                    'metadata': {
                        'nombre': 'test-empresa',
                        'lenguaje_principal': 'Python',
                        'lenguajes_analizados': ['Python', 'JavaScript'],
                        'archivos_analizados': 50
                    }
                },
                'candidato': {
                    'metadata': {
                        'nombre': 'test-candidato',
                        'lenguaje_principal': 'Python',
                        'lenguajes_analizados': ['Python'],
                        'archivos_analizados': 25
                    }
                }
            },
            'empathy_analysis': {
                'empathy_score': 75.5,
                'category_scores': {
                    'nombres': 80.0,
                    'documentacion': 70.0
                },
                'language_overlap': {
                    'score': 50.0,
                    'missing': ['JavaScript']
                },
                'recommendations': [
                    {
                        'title': 'Test Recommendation',
                        'description': 'Test description'
                    }
                ]
            }
        }
        
        # Should not raise any errors
        try:
            mostrar_resumen(test_results)
        except Exception as e:
            pytest.fail(f"mostrar_resumen raised an exception: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])