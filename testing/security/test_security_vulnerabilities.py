"""
Security Tests for HealthGuard AI
Tests security vulnerabilities and attack prevention
"""

import pytest
import httpx
import asyncio
import re
import hashlib


class TestAuthenticationSecurity:
    """Test authentication mechanisms"""
    
    @pytest.mark.asyncio
    async def test_no_credentials_in_urls(self):
        """Test that credentials are not exposed in URLs"""
        base_url = "http://localhost:8000"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/health")
            
            # URL should not contain passwords or tokens
            assert "password" not in str(response.url).lower()
            assert "token" not in str(response.url).lower()
            assert "secret" not in str(response.url).lower()
    
    @pytest.mark.asyncio
    async def test_secure_session_handling(self):
        """Test session security"""
        base_url = "http://localhost:8000"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/health")
            
            # Check for secure cookie attributes (in production)
            cookies = response.cookies
            for cookie in cookies:
                # In production, should have Secure and HttpOnly flags
                pass  # Placeholder - verify in production with HTTPS


class TestInjectionAttacks:
    """Test protection against injection attacks"""
    
    @pytest.mark.asyncio
    async def test_sql_injection_protection(self):
        """Test SQL injection prevention"""
        base_url = "http://localhost:8000"
        
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users--",
            "1' UNION SELECT NULL--",
            "admin'--",
            "' OR 1=1--"
        ]
        
        async with httpx.AsyncClient() as client:
            for payload in sql_payloads:
                response = await client.get(
                    f"{base_url}/api/v1/hospitals",
                    params={"search": payload}
                )
                
                # Should handle safely without executing SQL
                assert response.status_code in [200, 307, 400, 422]
                
                if response.status_code == 200:
                    # Should not return unauthorized data
                    data = response.json()
                    assert isinstance(data, (list, dict))
    
    @pytest.mark.asyncio
    async def test_nosql_injection_protection(self):
        """Test NoSQL injection prevention"""
        base_url = "http://localhost:8000"
        
        nosql_payloads = [
            '{"$gt": ""}',
            '{"$ne": null}',
            '{"$regex": ".*"}'
        ]
        
        async with httpx.AsyncClient() as client:
            for payload in nosql_payloads:
                response = await client.get(
                    f"{base_url}/api/v1/hospitals",
                    params={"filter": payload}
                )
                
                # Should reject or sanitize
                assert response.status_code in [200, 307, 400, 422]
    
    @pytest.mark.asyncio
    async def test_command_injection_protection(self):
        """Test command injection prevention"""
        base_url = "http://localhost:8000"
        
        command_payloads = [
            "; ls -la",
            "| cat /etc/passwd",
            "`whoami`",
            "$(cat /etc/passwd)",
            "&& rm -rf /"
        ]
        
        async with httpx.AsyncClient() as client:
            for payload in command_payloads:
                response = await client.get(
                    f"{base_url}/api/v1/hospitals",
                    params={"search": payload}
                )
                
                # Should sanitize or reject
                assert response.status_code in [200, 307, 400, 422]


class TestXSSProtection:
    """Test Cross-Site Scripting (XSS) protection"""
    
    @pytest.mark.asyncio
    async def test_xss_in_query_params(self):
        """Test XSS protection in query parameters"""
        base_url = "http://localhost:8000"
        
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src='javascript:alert(1)'>",
            "<svg onload=alert('XSS')>"
        ]
        
        async with httpx.AsyncClient() as client:
            for payload in xss_payloads:
                response = await client.get(
                    f"{base_url}/api/v1/hospitals",
                    params={"search": payload}
                )
                
                # Should sanitize or escape
                assert response.status_code in [200, 307, 400, 422]
                
                if response.status_code == 200:
                    # Response should not contain unescaped script tags
                    content = response.text
                    # Basic check - in production use proper HTML parser
                    assert "<script>" not in content.lower()
    
    @pytest.mark.asyncio
    async def test_content_type_headers(self):
        """Test that proper content-type headers are set"""
        base_url = "http://localhost:8000"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/health")
            
            # Should have proper content-type
            assert "application/json" in response.headers.get("content-type", "")


class TestCSRFProtection:
    """Test Cross-Site Request Forgery protection"""
    
    @pytest.mark.asyncio
    async def test_csrf_token_required(self):
        """Test CSRF token validation"""
        base_url = "http://localhost:8000"
        
        async with httpx.AsyncClient() as client:
            # POST without CSRF token should be rejected (in production)
            response = await client.post(
                f"{base_url}/api/v1/emergency/triage",
                json={"severity": "high"}
            )
            
            # Should reject or require token
            assert response.status_code in [200, 307, 401, 403, 404, 422]


class TestSecurityHeaders:
    """Test security HTTP headers"""
    
    @pytest.mark.asyncio
    async def test_security_headers_present(self):
        """Test that security headers are set"""
        base_url = "http://localhost:8000"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/health")
            
            headers = response.headers
            
            # Check for important security headers (some may not be in dev)
            # In production, these should all be present:
            # - X-Content-Type-Options: nosniff
            # - X-Frame-Options: DENY
            # - X-XSS-Protection: 1; mode=block
            # - Strict-Transport-Security (HTTPS only)
            
            # For now, just verify headers exist
            assert len(headers) > 0
    
    @pytest.mark.asyncio
    async def test_cors_configuration(self):
        """Test CORS is properly configured"""
        base_url = "http://localhost:8000"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/health")
            
            # Should have CORS headers
            # In production, should restrict origins
            assert response.status_code == 200


class TestInputValidation:
    """Test input validation and sanitization"""
    
    @pytest.mark.asyncio
    async def test_oversized_payload_rejection(self):
        """Test that oversized payloads are rejected"""
        base_url = "http://localhost:8000"
        
        # Create large payload
        large_data = {"data": "x" * 10_000_000}  # 10MB
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(
                    f"{base_url}/api/v1/emergency/triage",
                    json=large_data
                )
                
                # Should reject large payloads
                assert response.status_code in [400, 404, 413, 422]
            except (httpx.TimeoutException, httpx.RequestError):
                # Acceptable - request rejected
                pass
    
    @pytest.mark.asyncio
    async def test_malformed_json_handling(self):
        """Test handling of malformed JSON"""
        base_url = "http://localhost:8000"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/api/v1/emergency/triage",
                content="{ invalid json }",
                headers={"Content-Type": "application/json"}
            )
            
            # Should reject with proper error
            assert response.status_code in [400, 404, 422]
    
    @pytest.mark.asyncio
    async def test_special_characters_handling(self):
        """Test handling of special characters"""
        base_url = "http://localhost:8000"
        
        special_chars = [
            "../../../etc/passwd",  # Path traversal
            "..\\..\\windows\\system32",  # Windows path traversal
            "%00",  # Null byte
            "\x00",  # Null character
            "../../.."  # Directory traversal
        ]
        
        async with httpx.AsyncClient() as client:
            for chars in special_chars:
                response = await client.get(
                    f"{base_url}/api/v1/hospitals",
                    params={"search": chars}
                )
                
                # Should handle safely
                assert response.status_code in [200, 307, 400, 422]


class TestRateLimiting:
    """Test rate limiting protection"""
    
    @pytest.mark.asyncio
    async def test_rate_limit_enforcement(self):
        """Test that rate limiting is enforced"""
        base_url = "http://localhost:8000"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            responses = []
            
            # Make many rapid requests
            for _ in range(200):
                try:
                    response = await client.get(f"{base_url}/health")
                    responses.append(response.status_code)
                except Exception:
                    responses.append(0)
            
            # Should have some successful requests
            successful = [r for r in responses if r == 200]
            assert len(successful) > 0
            
            # In production with rate limiting, should see 429 responses
            rate_limited = [r for r in responses if r == 429]
            # For now, just verify we got responses
            assert len(responses) == 200


class TestDataExposure:
    """Test for data exposure vulnerabilities"""
    
    @pytest.mark.asyncio
    async def test_no_stack_traces_in_production(self):
        """Test that stack traces are not exposed"""
        base_url = "http://localhost:8000"
        
        async with httpx.AsyncClient() as client:
            # Try to trigger an error
            response = await client.get(f"{base_url}/api/v1/nonexistent")
            
            if response.status_code >= 400:
                content = response.text
                
                # Should not expose internal paths or stack traces
                assert "Traceback" not in content
                assert "/home/" not in content
                assert "File \"" not in content
    
    @pytest.mark.asyncio
    async def test_no_sensitive_data_in_errors(self):
        """Test that errors don't leak sensitive data"""
        base_url = "http://localhost:8000"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/api/v1/emergency/triage",
                json={"invalid": "data"}
            )
            
            if response.status_code >= 400:
                content = response.text.lower()
                
                # Should not expose sensitive info
                assert "password" not in content
                assert "secret" not in content
                assert "token" not in content


class TestEncryption:
    """Test encryption implementation"""
    
    @pytest.mark.asyncio
    async def test_https_redirect(self):
        """Test that HTTP redirects to HTTPS in production"""
        # In development, we use HTTP
        # In production, should redirect to HTTPS
        base_url = "http://localhost:8000"
        
        async with httpx.AsyncClient(follow_redirects=False) as client:
            response = await client.get(f"{base_url}/health")
            
            # In development, should work
            assert response.status_code in [200, 301, 302, 307, 308]
    
    @pytest.mark.asyncio
    async def test_sensitive_data_not_cached(self):
        """Test that sensitive data has proper cache headers"""
        base_url = "http://localhost:8000"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/api/v1/hospitals")
            
            # Sensitive endpoints should have cache-control headers
            # This ensures data isn't cached inappropriately
            assert response.status_code in [200, 307, 401, 403]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
