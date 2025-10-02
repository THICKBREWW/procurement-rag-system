"""
Input validation utilities for the Procurement RAG System
"""

import re
import os
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

# Import configuration
try:
    from config import CONTRACT_TYPES, DOCUMENT_TYPES, ALLOWED_EXTENSIONS, MAX_FILE_SIZE
except ImportError:
    # Fallback configuration
    CONTRACT_TYPES = ["service", "procurement", "vendor", "software", "consulting", "construction", "general"]
    DOCUMENT_TYPES = ["policy", "vendor", "compliance"]
    ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

class ValidationError(Exception):
    """Base validation error"""
    pass

def validate_not_empty(value: Any, field_name: str) -> None:
    """Validate that a value is not empty"""
    if not value or (isinstance(value, str) and not value.strip()):
        raise ValidationError(f"{field_name} cannot be empty")

def validate_contract_type(contract_type: str) -> None:
    """Validate contract type"""
    if contract_type not in CONTRACT_TYPES:
        raise ValidationError(f"Invalid contract type. Must be one of: {', '.join(CONTRACT_TYPES)}")

def validate_contract_text(contract_text: str) -> None:
    """Validate contract text"""
    validate_not_empty(contract_text, "Contract text")
    if len(contract_text) < 50:
        raise ValidationError("Contract text must be at least 50 characters long")

def validate_document_type(doc_type: str) -> None:
    """Validate document type"""
    if doc_type not in DOCUMENT_TYPES:
        raise ValidationError(f"Invalid document type. Must be one of: {', '.join(DOCUMENT_TYPES)}")

def validate_file_extension(filename: str) -> None:
    """Validate file extension"""
    if not filename:
        raise ValidationError("Filename cannot be empty")
    
    ext = Path(filename).suffix.lower().lstrip('.')
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(f"File type '{ext}' not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}")

def validate_contract_input(contract_text: str, contract_type: str = "general") -> Dict[str, Any]:
    """Comprehensive contract input validation"""
    errors = []
    warnings = []
    
    try:
        validate_contract_text(contract_text)
    except ValidationError as e:
        errors.append(str(e))
    
    try:
        validate_contract_type(contract_type)
    except ValidationError as e:
        errors.append(str(e))
    
    if len(contract_text) < 100:
        warnings.append("Contract text is very short - may not contain sufficient detail")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }