#!/usr/bin/env python3
"""
Vector Database Setup Script for Cultural Context Service

This script sets up and configures the vector database for the Cultural Context Service.
It supports Pinecone, Weaviate, and in-memory fallback options.

Usage:
    python setup_vector_db.py --provider pinecone --create-index
    python setup_vector_db.py --provider weaviate --test-connection
    python setup_vector_db.py --provider memory --index-kb
"""

import os
import sys
import json
import argparse
import logging
from typing import Dict, Any, List, Optional

# Add the service root to Python path
service_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, service_root)

from services.rag_service import get_rag_service
from services.embeddings import get_embedding_service

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class VectorDBSetup:
    """Vector database setup and configuration utility"""
    
    def __init__(self):
        self.rag_service = get_rag_service()
        self.embedding_service = get_embedding_service()
    
    def check_dependencies(self) -> Dict[str, bool]:
        """Check if required dependencies are available"""
        deps = {}
        
        # Check Pinecone
        try:
            import pinecone
            deps['pinecone'] = True
        except ImportError:
            deps['pinecone'] = False
        
        # Check Weaviate
        try:
            import weaviate
            deps['weaviate'] = True
        except ImportError:
            deps['weaviate'] = False
        
        # Check OpenAI
        try:
            import openai
            deps['openai'] = True
        except ImportError:
            deps['openai'] = False
        
        # Check sentence-transformers
        try:
            import sentence_transformers
            deps['sentence_transformers'] = True
        except ImportError:
            deps['sentence_transformers'] = False
        
        return deps
    
    def check_environment_variables(self, provider: str) -> Dict[str, Any]:
        """Check if required environment variables are set"""
        env_status = {}
        
        if provider == "pinecone":
            env_status['PINECONE_API_KEY'] = {
                'value': os.getenv('PINECONE_API_KEY', ''),
                'required': True,
                'set': bool(os.getenv('PINECONE_API_KEY'))
            }
            env_status['PINECONE_INDEX_NAME'] = {
                'value': os.getenv('PINECONE_INDEX_NAME', 'cultural-context'),
                'required': False,
                'set': True  # Has default
            }
        
        elif provider == "weaviate":
            env_status['WEAVIATE_URL'] = {
                'value': os.getenv('WEAVIATE_URL', ''),
                'required': True,
                'set': bool(os.getenv('WEAVIATE_URL'))
            }
            env_status['WEAVIATE_API_KEY'] = {
                'value': os.getenv('WEAVIATE_API_KEY', ''),
                'required': False,
                'set': bool(os.getenv('WEAVIATE_API_KEY'))
            }
        
        # Common embedding service variables
        env_status['OPENAI_API_KEY'] = {
            'value': os.getenv('OPENAI_API_KEY', ''),
            'required': False,
            'set': bool(os.getenv('OPENAI_API_KEY'))
        }
        
        return env_status
    
    def test_connection(self, provider: str) -> Dict[str, Any]:
        """Test connection to vector database"""
        logger.info(f"Testing connection to {provider}...")
        
        try:
            connection_status = self.rag_service.check_connection()
            
            if connection_status.get("connected"):
                logger.info(f"✅ Successfully connected to {provider}")
                return {
                    "success": True,
                    "provider": provider,
                    "status": connection_status
                }
            else:
                logger.error(f"❌ Failed to connect to {provider}")
                return {
                    "success": False,
                    "provider": provider,
                    "status": connection_status,
                    "error": connection_status.get("error", "Connection failed")
                }
                
        except Exception as e:
            logger.error(f"❌ Connection test failed: {e}")
            return {
                "success": False,
                "provider": provider,
                "error": str(e)
            }
    
    def create_index(self, provider: str, dimension: Optional[int] = None) -> Dict[str, Any]:
        """Create vector database index"""
        logger.info(f"Creating index for {provider}...")
        
        try:
            if provider == "pinecone":
                success = self.rag_service.ensure_index_exists(dimension=dimension)
                if success:
                    logger.info("✅ Pinecone index created successfully")
                    stats = self.rag_service.get_index_stats()
                    return {
                        "success": True,
                        "provider": provider,
                        "stats": stats
                    }
                else:
                    logger.error("❌ Failed to create Pinecone index")
                    return {
                        "success": False,
                        "provider": provider,
                        "error": "Failed to create index"
                    }
            
            elif provider == "weaviate":
                # Weaviate schema is created automatically in RAG service
                connection_status = self.rag_service.check_connection()
                if connection_status.get("connected"):
                    logger.info("✅ Weaviate schema ready")
                    return {
                        "success": True,
                        "provider": provider,
                        "status": connection_status
                    }
                else:
                    logger.error("❌ Weaviate connection failed")
                    return {
                        "success": False,
                        "provider": provider,
                        "error": "Connection failed"
                    }
            
            else:
                logger.info("✅ In-memory storage ready")
                return {
                    "success": True,
                    "provider": "memory"
                }
                
        except Exception as e:
            logger.error(f"❌ Index creation failed: {e}")
            return {
                "success": False,
                "provider": provider,
                "error": str(e)
            }
    
    def index_knowledge_base(self, clear_existing: bool = False) -> Dict[str, Any]:
        """Index the cultural knowledge base"""
        logger.info("Indexing cultural knowledge base...")
        
        try:
            # Clear existing if requested
            if clear_existing:
                logger.info("Clearing existing vectors...")
                if self.rag_service.clear_index():
                    logger.info("✅ Existing vectors cleared")
                else:
                    logger.warning("⚠️ Failed to clear existing vectors")
            
            # Load knowledge base
            kb_path = os.path.join(service_root, "data", "kb.json")
            if not os.path.exists(kb_path):
                logger.error(f"❌ Knowledge base file not found: {kb_path}")
                return {
                    "success": False,
                    "error": "Knowledge base file not found"
                }
            
            with open(kb_path, 'r', encoding='utf-8') as f:
                kb_data = json.load(f)
            
            kb_entries = kb_data.get("entries", [])
            if not kb_entries:
                logger.warning("⚠️ No entries found in knowledge base")
                return {
                    "success": True,
                    "indexed_count": 0,
                    "total_entries": 0,
                    "message": "No entries to index"
                }
            
            # Index entries
            logger.info(f"Indexing {len(kb_entries)} entries...")
            indexed_count = self.rag_service.index_knowledge_base(kb_entries)
            
            # Get final stats
            stats = self.rag_service.get_index_stats()
            
            logger.info(f"✅ Successfully indexed {indexed_count}/{len(kb_entries)} entries")
            
            return {
                "success": True,
                "indexed_count": indexed_count,
                "total_entries": len(kb_entries),
                "stats": stats
            }
            
        except Exception as e:
            logger.error(f"❌ Knowledge base indexing failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status of vector database setup"""
        logger.info("Getting vector database status...")
        
        status = {
            "timestamp": "2025-01-12T00:00:00Z",
            "dependencies": self.check_dependencies(),
            "embedding_service": {
                "available": self.embedding_service.is_available(),
                "type": getattr(self.embedding_service, 'service_type', 'unknown')
            },
            "vector_db": self.rag_service.check_connection(),
            "index_stats": self.rag_service.get_index_stats()
        }
        
        # Check environment variables for current provider
        provider = self.rag_service.vector_db_type or "memory"
        status["environment"] = self.check_environment_variables(provider)
        
        return status


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Vector Database Setup for Cultural Context Service")
    parser.add_argument("--provider", choices=["pinecone", "weaviate", "memory"], 
                       help="Vector database provider")
    parser.add_argument("--create-index", action="store_true", 
                       help="Create vector database index")
    parser.add_argument("--test-connection", action="store_true", 
                       help="Test connection to vector database")
    parser.add_argument("--index-kb", action="store_true", 
                       help="Index knowledge base")
    parser.add_argument("--clear-existing", action="store_true", 
                       help="Clear existing vectors before indexing")
    parser.add_argument("--status", action="store_true", 
                       help="Show comprehensive status")
    parser.add_argument("--dimension", type=int, 
                       help="Embedding dimension for index creation")
    
    args = parser.parse_args()
    
    setup = VectorDBSetup()
    
    if args.status:
        status = setup.get_status()
        print(json.dumps(status, indent=2))
        return
    
    if not args.provider and not args.status:
        # Auto-detect provider
        args.provider = setup.rag_service.vector_db_type or "memory"
        logger.info(f"Auto-detected provider: {args.provider}")
    
    if args.test_connection:
        result = setup.test_connection(args.provider)
        print(json.dumps(result, indent=2))
        if not result["success"]:
            sys.exit(1)
    
    if args.create_index:
        result = setup.create_index(args.provider, dimension=args.dimension)
        print(json.dumps(result, indent=2))
        if not result["success"]:
            sys.exit(1)
    
    if args.index_kb:
        result = setup.index_knowledge_base(clear_existing=args.clear_existing)
        print(json.dumps(result, indent=2))
        if not result["success"]:
            sys.exit(1)
    
    logger.info("✅ Vector database setup completed successfully")


if __name__ == "__main__":
    main()