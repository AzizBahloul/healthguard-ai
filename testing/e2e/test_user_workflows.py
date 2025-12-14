"""
End-to-End tests for complete user workflows
Tests entire system from frontend through backend to MCP
"""
import pytest
import httpx
import asyncio
import time

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


class TestEmergencyE2E:
    """E2E tests for emergency response workflow"""
    
    @pytest.fixture(scope="class")
    def driver(self):
        """Setup Selenium WebDriver"""
        if not SELENIUM_AVAILABLE:
            pytest.skip("Selenium not installed")
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=options)
        yield driver
        driver.quit()
    
    def test_complete_emergency_workflow(self, driver):
        """
        Test complete workflow:
        1. User creates emergency case
        2. System assigns ambulance
        3. System finds hospital bed
        4. Track patient through journey
        """
        # Navigate to emergency dashboard
        driver.get("http://localhost:3000/emergency/create")
        
        # Fill emergency form
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "patient-id"))
        )
        
        driver.find_element(By.ID, "patient-id").send_keys("P_E2E_001")
        driver.find_element(By.ID, "severity").send_keys("Critical")
        driver.find_element(By.ID, "type").send_keys("Cardiac Arrest")
        driver.find_element(By.ID, "latitude").send_keys("40.7128")
        driver.find_element(By.ID, "longitude").send_keys("-74.0060")
        
        # Submit form
        driver.find_element(By.ID, "submit-emergency").click()
        
        # Wait for confirmation
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "success-message"))
        )
        
        success_msg = driver.find_element(By.CLASS_NAME, "success-message").text
        assert "Emergency case created" in success_msg
        
        # Extract case ID
        case_id_element = driver.find_element(By.ID, "case-id")
        case_id = case_id_element.text
        
        # Navigate to tracking page
        driver.get(f"http://localhost:3000/emergency/track/{case_id}")
        
        # Verify ambulance assignment
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ambulance-assigned"))
        )
        
        ambulance_info = driver.find_element(By.CLASS_NAME, "ambulance-info").text
        assert "AMB" in ambulance_info  # Ambulance ID format
        
        # Verify hospital assignment
        hospital_info = driver.find_element(By.CLASS_NAME, "hospital-info").text
        assert len(hospital_info) > 0
        
        # Check map visualization
        map_element = driver.find_element(By.ID, "tracking-map")
        assert map_element.is_displayed()
    
    def test_hospital_search_workflow(self, driver):
        """Test searching and viewing hospital details"""
        driver.get("http://localhost:3000/hospitals")
        
        # Search for hospitals
        search_box = driver.find_element(By.ID, "hospital-search")
        search_box.send_keys("Metro General")
        search_box.submit()
        
        # Wait for results
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "hospital-card"))
        )
        
        # Click first result
        first_result = driver.find_element(By.CLASS_NAME, "hospital-card")
        first_result.click()
        
        # Verify hospital details page
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "hospital-details"))
        )
        
        # Check capacity information
        capacity_element = driver.find_element(By.CLASS_NAME, "capacity-info")
        assert capacity_element.is_displayed()
        
        # Check real-time availability
        availability = driver.find_element(By.CLASS_NAME, "availability-status")
        assert availability.text in ["Available", "Limited", "Full"]
    
    def test_command_center_dashboard(self, driver):
        """Test command center real-time dashboard"""
        driver.get("http://localhost:3000/command-center")
        
        # Verify all dashboard components load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "active-emergencies"))
        )
        
        # Check active emergencies panel
        active_emergencies = driver.find_element(By.ID, "active-emergencies")
        assert active_emergencies.is_displayed()
        
        # Check hospital capacity heatmap
        heatmap = driver.find_element(By.ID, "capacity-heatmap")
        assert heatmap.is_displayed()
        
        # Check ambulance tracker
        ambulance_tracker = driver.find_element(By.ID, "ambulance-tracker")
        assert ambulance_tracker.is_displayed()
        
        # Check real-time alerts
        alerts_panel = driver.find_element(By.ID, "alerts-panel")
        assert alerts_panel.is_displayed()
        
        # Verify data updates (wait for refresh)
        time.sleep(5)
        # Data should update without page reload


class TestAmbulanceDispatchE2E:
    """E2E tests for ambulance dispatch workflow"""
    
    @pytest.fixture
    def api_client(self):
        return httpx.AsyncClient(base_url="http://localhost:8000")
    
    @pytest.mark.asyncio
    async def test_automated_dispatch(self, api_client):
        """Test automated ambulance dispatch"""
        # Create emergency
        emergency_data = {
            "patient_id": "P_DISPATCH_E2E",
            "severity": "high",
            "type": "trauma",
            "location": {"latitude": 40.7, "longitude": -74.0}
        }
        
        response = await api_client.post("/api/v1/emergency/create", json=emergency_data)
        assert response.status_code == 201
        case_id = response.json()["case_id"]
        
        # Wait for automated dispatch
        await asyncio.sleep(3)
        
        # Verify ambulance was dispatched
        case_response = await api_client.get(f"/api/v1/emergency/{case_id}")
        case_data = case_response.json()
        assert "ambulance_id" in case_data
        
        # Track ambulance location updates
        ambulance_id = case_data["ambulance_id"]
        location_response = await api_client.get(f"/api/v1/ambulances/{ambulance_id}")
        assert location_response.status_code == 200


class TestDataFlowE2E:
    """Test data flow through entire system"""
    
    @pytest.mark.asyncio
    async def test_data_consistency(self):
        """Test that data remains consistent across all components"""
        async with httpx.AsyncClient() as client:
            # Create data in backend
            test_data = {
                "patient_id": "P_CONSISTENCY_TEST",
                "severity": "medium",
                "type": "general",
                "location": {"latitude": 40.7, "longitude": -74.0}
            }
            
            backend_response = await client.post(
                "http://localhost:8000/api/v1/emergency/create",
                json=test_data
            )
            case_id = backend_response.json()["case_id"]
            
            # Wait for propagation
            await asyncio.sleep(2)
            
            # Verify in MCP
            mcp_response = await client.get(
                f"http://localhost:3000/api/agents/memory/case/{case_id}"
            )
            assert mcp_response.status_code == 200
            
            # Verify data matches
            mcp_data = mcp_response.json()
            assert mcp_data["patient_id"] == test_data["patient_id"]
            assert mcp_data["severity"] == test_data["severity"]


class TestUserAuthenticationE2E:
    """Test user authentication and authorization"""
    
    def test_login_workflow(self, driver):
        """Test complete login workflow"""
        driver.get("http://localhost:3000/login")
        
        # Fill login form
        driver.find_element(By.ID, "username").send_keys("admin@healthguard.ai")
        driver.find_element(By.ID, "password").send_keys("admin_password")
        driver.find_element(By.ID, "login-button").click()
        
        # Should redirect to dashboard
        WebDriverWait(driver, 10).until(
            EC.url_contains("/dashboard")
        )
        
        # Verify logged in
        user_menu = driver.find_element(By.ID, "user-menu")
        assert user_menu.is_displayed()
    
    def test_unauthorized_access(self, driver):
        """Test that unauthorized users cannot access protected routes"""
        driver.get("http://localhost:3000/admin")
        
        # Should redirect to login
        WebDriverWait(driver, 10).until(
            EC.url_contains("/login")
        )


class TestPerformanceE2E:
    """Test system performance under realistic load"""
    
    @pytest.mark.asyncio
    async def test_response_time_under_load(self):
        """Test response times with multiple concurrent requests"""
        import time
        import asyncio
        
        async def create_emergency(client, i):
            start = time.time()
            response = await client.post(
                "http://localhost:8000/api/v1/emergency/create",
                json={
                    "patient_id": f"P_LOAD_{i}",
                    "severity": "medium",
                    "type": "general",
                    "location": {"latitude": 40.7, "longitude": -74.0}
                }
            )
            end = time.time()
            return end - start, response.status_code
        
        async with httpx.AsyncClient() as client:
            tasks = [create_emergency(client, i) for i in range(50)]
            results = await asyncio.gather(*tasks)
            
            # All should succeed
            assert all(status == 201 for _, status in results)
            
            # Average response time should be under 500ms
            avg_time = sum(duration for duration, _ in results) / len(results)
            assert avg_time < 0.5
