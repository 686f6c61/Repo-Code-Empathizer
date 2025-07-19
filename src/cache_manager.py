"""
Módulo de gestión de caché para resultados de análisis.

Este módulo implementa un sistema de caché persistente para almacenar
y recuperar resultados de análisis de repositorios, evitando análisis
repetitivos y mejorando el rendimiento de la aplicación.

Classes:
    CacheManager: Gestor principal de caché con TTL configurable.
    CachedAnalyzer: Analizador con capacidad de caché integrada.

Features:
    - Caché persistente en disco con formato JSON
    - TTL (Time To Live) configurable
    - Gestión automática de expiración
    - Limpieza de caché antigua
    - Información detallada sobre uso del caché

Author: R. Benítez
Version: 2.0.0
License: MIT
"""
import json
import os
import hashlib
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages cache for repository analysis results"""
    
    def __init__(self, cache_dir: str = "cache", ttl_hours: int = 24):
        """Initialize cache manager
        
        Args:
            cache_dir: Directory to store cache files
            ttl_hours: Time to live for cache entries in hours
        """
        self.cache_dir = cache_dir
        self.ttl_hours = ttl_hours
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self):
        """Ensure cache directory exists"""
        os.makedirs(self.cache_dir, exist_ok=True)
        # Create metadata file if it doesn't exist
        metadata_path = os.path.join(self.cache_dir, "metadata.json")
        if not os.path.exists(metadata_path):
            with open(metadata_path, 'w') as f:
                json.dump({}, f)
    
    def get_cache_key(self, repo_name: str, commit_hash: Optional[str] = None) -> str:
        """Generate cache key for a repository
        
        Args:
            repo_name: Repository name (owner/repo)
            commit_hash: Optional commit hash for specific version
            
        Returns:
            Cache key string
        """
        if commit_hash:
            key_string = f"{repo_name}:{commit_hash}"
        else:
            key_string = repo_name
        
        # Create a hash for the filename
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, repo_name: str, commit_hash: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get cached analysis results
        
        Args:
            repo_name: Repository name
            commit_hash: Optional commit hash
            
        Returns:
            Cached analysis results or None if not found/expired
        """
        cache_key = self.get_cache_key(repo_name, commit_hash)
        cache_path = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            with open(cache_path, 'r') as f:
                cached_data = json.load(f)
            
            # Check if cache is expired
            cached_time = datetime.fromisoformat(cached_data['timestamp'])
            if datetime.now() - cached_time > timedelta(hours=self.ttl_hours):
                logger.info(f"Cache expired for {repo_name}")
                self.delete(repo_name, commit_hash)
                return None
            
            logger.info(f"Cache hit for {repo_name}")
            return cached_data['data']
            
        except Exception as e:
            logger.error(f"Error reading cache for {repo_name}: {e}")
            return None
    
    def set(self, repo_name: str, data: Dict[str, Any], commit_hash: Optional[str] = None):
        """Store analysis results in cache
        
        Args:
            repo_name: Repository name
            data: Analysis results to cache
            commit_hash: Optional commit hash
        """
        cache_key = self.get_cache_key(repo_name, commit_hash)
        cache_path = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'repo_name': repo_name,
                'commit_hash': commit_hash,
                'data': data
            }
            
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            # Update metadata
            self._update_metadata(repo_name, cache_key, commit_hash)
            
            logger.info(f"Cached analysis results for {repo_name}")
            
        except Exception as e:
            logger.error(f"Error caching results for {repo_name}: {e}")
    
    def delete(self, repo_name: str, commit_hash: Optional[str] = None):
        """Delete cached results for a repository
        
        Args:
            repo_name: Repository name
            commit_hash: Optional commit hash
        """
        cache_key = self.get_cache_key(repo_name, commit_hash)
        cache_path = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        if os.path.exists(cache_path):
            os.remove(cache_path)
            logger.info(f"Deleted cache for {repo_name}")
            
        # Update metadata
        self._remove_from_metadata(cache_key)
    
    def clear_all(self):
        """Clear all cached data"""
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json') and filename != 'metadata.json':
                os.remove(os.path.join(self.cache_dir, filename))
        
        # Clear metadata
        with open(os.path.join(self.cache_dir, "metadata.json"), 'w') as f:
            json.dump({}, f)
        
        logger.info("Cleared all cache")
    
    def clear_expired(self):
        """Clear only expired cache entries"""
        metadata_path = os.path.join(self.cache_dir, "metadata.json")
        
        try:
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            expired_keys = []
            for cache_key, info in metadata.items():
                cached_time = datetime.fromisoformat(info['timestamp'])
                if datetime.now() - cached_time > timedelta(hours=self.ttl_hours):
                    # Delete cache file
                    cache_path = os.path.join(self.cache_dir, f"{cache_key}.json")
                    if os.path.exists(cache_path):
                        os.remove(cache_path)
                    expired_keys.append(cache_key)
            
            # Update metadata
            for key in expired_keys:
                metadata.pop(key, None)
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Cleared {len(expired_keys)} expired cache entries")
            
        except Exception as e:
            logger.error(f"Error clearing expired cache: {e}")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about cached data
        
        Returns:
            Dictionary with cache statistics
        """
        metadata_path = os.path.join(self.cache_dir, "metadata.json")
        
        try:
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            total_size = 0
            file_count = 0
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.cache_dir, filename)
                    total_size += os.path.getsize(file_path)
                    file_count += 1
            
            return {
                'total_entries': len(metadata),
                'total_files': file_count,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'cache_dir': self.cache_dir,
                'ttl_hours': self.ttl_hours
            }
            
        except Exception as e:
            logger.error(f"Error getting cache info: {e}")
            return {}
    
    def _update_metadata(self, repo_name: str, cache_key: str, commit_hash: Optional[str]):
        """Update cache metadata"""
        metadata_path = os.path.join(self.cache_dir, "metadata.json")
        
        try:
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            metadata[cache_key] = {
                'repo_name': repo_name,
                'commit_hash': commit_hash,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error updating metadata: {e}")
    
    def _remove_from_metadata(self, cache_key: str):
        """Remove entry from metadata"""
        metadata_path = os.path.join(self.cache_dir, "metadata.json")
        
        try:
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            metadata.pop(cache_key, None)
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error removing from metadata: {e}")


class CachedAnalyzer:
    """Analyzer wrapper with caching support"""
    
    def __init__(self, cache_manager: CacheManager, analyzer):
        self.cache_manager = cache_manager
        self.analyzer = analyzer
    
    def analyze_repo(self, repo_name: str, commit_hash: Optional[str] = None, force: bool = False) -> Dict[str, Any]:
        """Analyze repository with caching
        
        Args:
            repo_name: Repository name
            commit_hash: Optional commit hash
            force: Force re-analysis even if cached
            
        Returns:
            Analysis results
        """
        # Check cache first
        if not force:
            cached_result = self.cache_manager.get(repo_name, commit_hash)
            if cached_result:
                return cached_result
        
        # Perform analysis
        result = self.analyzer.analizar_repo(repo_name)
        
        # Cache the result
        if result:
            self.cache_manager.set(repo_name, result, commit_hash)
        
        return result