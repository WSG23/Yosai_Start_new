from security.auth_service import SecurityService


def test_security_service_methods():
    service = SecurityService(config=None)

    # methods should exist and return None or default values
    assert service.enable_input_validation() is None
    assert service.enable_rate_limiting() is None
    assert service.enable_file_validation() is None
    assert service.validate_file("test.txt", 10) == {"valid": True}
    service.log_file_processing_event("test.txt", success=True)
    assert service.get_security_status() == {
        "input_validation": False,
        "rate_limiting": False,
        "file_validation": False,
    }
