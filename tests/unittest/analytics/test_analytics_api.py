"""
Unit tests for Analytics API
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta
from fastapi import HTTPException


class TestAnalyticsAPI:
    """Test suite for Analytics API endpoints"""
    
    @pytest.fixture
    def mock_user(self):
        """Create a mock user"""
        user = Mock()
        user.id = "user_123"
        return user
    
    @pytest.fixture
    def mock_db_connection(self):
        """Create a mock database connection"""
        conn = Mock()
        cursor = Mock()
        conn.cursor.return_value.__enter__ = Mock(return_value=cursor)
        conn.cursor.return_value.__exit__ = Mock(return_value=False)
        return conn, cursor
    
    @pytest.mark.asyncio
    @patch('app.api.analytics.db_manager.get_connection')
    async def test_get_document_uploads_over_time_7d(self, mock_get_conn, mock_user, mock_db_connection):
        """Test document uploads analytics for 7 days"""
        from app.api.analytics import get_document_uploads_over_time
        
        conn, cursor = mock_db_connection
        mock_get_conn.return_value.__enter__ = Mock(return_value=conn)
        mock_get_conn.return_value.__exit__ = Mock(return_value=False)
        
        # Mock query results
        cursor.fetchall.side_effect = [
            [(datetime.now().date(), 5, 1024000)],  # Chart data
            [(10, 5120000, 512000, datetime.now(), datetime.now())]  # Summary
        ]
        
        result = await get_document_uploads_over_time(period="7d", current_user=mock_user)
        
        assert "chartData" in result
        assert "summary" in result
        assert result["period"] == "7d"
        assert result["summary"]["totalDocuments"] == 10
    
    @pytest.mark.asyncio
    @patch('app.api.analytics.db_manager.get_connection')
    async def test_get_document_uploads_over_time_30d(self, mock_get_conn, mock_user, mock_db_connection):
        """Test document uploads analytics for 30 days"""
        from app.api.analytics import get_document_uploads_over_time
        
        conn, cursor = mock_db_connection
        mock_get_conn.return_value.__enter__ = Mock(return_value=conn)
        mock_get_conn.return_value.__exit__ = Mock(return_value=False)
        
        cursor.fetchall.side_effect = [
            [(datetime.now().date(), 15, 2048000)],
            [(50, 10240000, 204800, datetime.now(), datetime.now())]
        ]
        
        result = await get_document_uploads_over_time(period="30d", current_user=mock_user)
        
        assert result["period"] == "30d"
        assert len(result["chartData"]) > 0
    
    @pytest.mark.asyncio
    async def test_get_document_uploads_invalid_period(self, mock_user):
        """Test with invalid period parameter"""
        from app.api.analytics import get_document_uploads_over_time
        
        with pytest.raises(HTTPException) as exc_info:
            await get_document_uploads_over_time(period="invalid", current_user=mock_user)
        
        assert exc_info.value.status_code == 400
    
    @pytest.mark.asyncio
    async def test_get_document_uploads_invalid_user(self):
        """Test with invalid user"""
        from app.api.analytics import get_document_uploads_over_time
        
        invalid_user = Mock()
        invalid_user.id = None
        
        with pytest.raises(HTTPException) as exc_info:
            await get_document_uploads_over_time(period="7d", current_user=invalid_user)
        
        assert exc_info.value.status_code == 400
    
    @pytest.mark.asyncio
    @patch('app.api.analytics.db_manager.get_connection')
    async def test_get_document_types_distribution(self, mock_get_conn, mock_user, mock_db_connection):
        """Test document types distribution"""
        from app.api.analytics import get_document_types_distribution
        
        conn, cursor = mock_db_connection
        mock_get_conn.return_value.__enter__ = Mock(return_value=conn)
        mock_get_conn.return_value.__exit__ = Mock(return_value=False)
        
        cursor.fetchall.return_value = [
            ("research paper", 10, 512000),
            ("legal docs", 5, 1024000),
            ("invoices", 3, 256000)
        ]
        
        result = await get_document_types_distribution(current_user=mock_user)
        
        assert "chartData" in result
        assert len(result["chartData"]) == 3
        assert result["chartData"][0]["type"] == "research paper"
        assert result["chartData"][0]["count"] == 10
    
    @pytest.mark.asyncio
    @patch('app.api.analytics.db_manager.get_connection')
    async def test_get_document_types_distribution_with_unknown(self, mock_get_conn, mock_user, mock_db_connection):
        """Test document types distribution with unknown types"""
        from app.api.analytics import get_document_types_distribution
        
        conn, cursor = mock_db_connection
        mock_get_conn.return_value.__enter__ = Mock(return_value=conn)
        mock_get_conn.return_value.__exit__ = Mock(return_value=False)
        
        cursor.fetchall.return_value = [
            (None, 5, 512000),  # Unknown type
            ("research paper", 10, 1024000)
        ]
        
        result = await get_document_types_distribution(current_user=mock_user)
        
        assert result["chartData"][0]["type"] == "Unknown"
    
    @pytest.mark.asyncio
    @patch('app.api.analytics.db_manager.get_connection')
    async def test_get_upload_trends(self, mock_get_conn, mock_user, mock_db_connection):
        """Test upload trends by day and hour"""
        from app.api.analytics import get_upload_trends
        
        conn, cursor = mock_db_connection
        mock_get_conn.return_value.__enter__ = Mock(return_value=conn)
        mock_get_conn.return_value.__exit__ = Mock(return_value=False)
        
        cursor.fetchall.side_effect = [
            [(0, 5), (1, 10), (2, 8)],  # Day of week
            [(9, 15), (14, 20), (18, 10)]  # Hour of day
        ]
        
        result = await get_upload_trends(current_user=mock_user)
        
        assert "byDayOfWeek" in result
        assert "byHourOfDay" in result
        assert len(result["byDayOfWeek"]) == 3
        assert result["byDayOfWeek"][0]["day"] == "Sunday"
        assert result["byHourOfDay"][0]["hour"] == "09:00"
    
    @pytest.mark.asyncio
    @patch('app.api.analytics.db_manager.get_connection')
    async def test_get_storage_usage(self, mock_get_conn, mock_user, mock_db_connection):
        """Test storage usage statistics"""
        from app.api.analytics import get_storage_usage
        
        conn, cursor = mock_db_connection
        mock_get_conn.return_value.__enter__ = Mock(return_value=conn)
        mock_get_conn.return_value.__exit__ = Mock(return_value=False)
        
        used_storage = 100 * 1024 * 1024  # 100MB
        cursor.fetchone.return_value = (used_storage,)
        
        result = await get_storage_usage(current_user=mock_user)
        
        assert "totalStorage" in result
        assert "usedStorage" in result
        assert "availableStorage" in result
        assert "usagePercentage" in result
        assert result["usedStorage"] == used_storage
        assert result["usagePercentage"] > 0
    
    @pytest.mark.asyncio
    @patch('app.api.analytics.db_manager.get_connection')
    async def test_get_storage_usage_empty(self, mock_get_conn, mock_user, mock_db_connection):
        """Test storage usage with no documents"""
        from app.api.analytics import get_storage_usage
        
        conn, cursor = mock_db_connection
        mock_get_conn.return_value.__enter__ = Mock(return_value=conn)
        mock_get_conn.return_value.__exit__ = Mock(return_value=False)
        
        cursor.fetchone.return_value = (None,)
        
        result = await get_storage_usage(current_user=mock_user)
        
        assert result["usedStorage"] == 0
        assert result["usagePercentage"] == 0
    
    @pytest.mark.asyncio
    @patch('app.api.analytics.db_manager.get_connection')
    async def test_get_model_usage_over_time(self, mock_get_conn, mock_user, mock_db_connection):
        """Test model usage statistics"""
        from app.api.analytics import get_model_usage_over_time
        
        conn, cursor = mock_db_connection
        mock_get_conn.return_value.__enter__ = Mock(return_value=conn)
        mock_get_conn.return_value.__exit__ = Mock(return_value=False)
        
        cursor.fetchall.return_value = [
            (datetime.now().date(), "bart", 10),
            (datetime.now().date(), "pegasus", 5),
            (datetime.now().date(), "t5", 3)
        ]
        
        result = await get_model_usage_over_time(period="30d", current_user=mock_user)
        
        assert "models" in result
        assert "period" in result
        assert "bart" in result["models"]
        assert "pegasus" in result["models"]
    
    @pytest.mark.asyncio
    @patch('app.api.analytics.db_manager.get_connection')
    async def test_get_model_usage_bart_mapping(self, mock_get_conn, mock_user, mock_db_connection):
        """Test that facebook/bart-large-cnn is mapped to t5"""
        from app.api.analytics import get_model_usage_over_time
        
        conn, cursor = mock_db_connection
        mock_get_conn.return_value.__enter__ = Mock(return_value=conn)
        mock_get_conn.return_value.__exit__ = Mock(return_value=False)
        
        cursor.fetchall.return_value = [
            (datetime.now().date(), "t5", 15)  # Mapped from facebook/bart-large-cnn
        ]
        
        result = await get_model_usage_over_time(period="7d", current_user=mock_user)
        
        assert "t5" in result["models"]
    
    @pytest.mark.asyncio
    @patch('app.api.analytics.db_manager.get_connection')
    async def test_get_ocr_confidence_distribution(self, mock_get_conn, mock_user, mock_db_connection):
        """Test OCR confidence distribution"""
        from app.api.analytics import get_ocr_confidence_distribution
        
        conn, cursor = mock_db_connection
        mock_get_conn.return_value.__enter__ = Mock(return_value=conn)
        mock_get_conn.return_value.__exit__ = Mock(return_value=False)
        
        cursor.fetchall.return_value = [
            (0.45,), (0.65,), (0.75,), (0.88,), (0.96,), (0.98,)
        ]
        
        result = await get_ocr_confidence_distribution(current_user=mock_user)
        
        assert "scores" in result
        assert "distribution" in result
        assert "statistics" in result
        assert len(result["scores"]) == 6
        assert "low" in result["distribution"]
        assert "excellent" in result["distribution"]
        assert result["statistics"]["total"] == 6
    
    @pytest.mark.asyncio
    @patch('app.api.analytics.db_manager.get_connection')
    async def test_get_ocr_confidence_distribution_empty(self, mock_get_conn, mock_user, mock_db_connection):
        """Test OCR confidence distribution with no data"""
        from app.api.analytics import get_ocr_confidence_distribution
        
        conn, cursor = mock_db_connection
        mock_get_conn.return_value.__enter__ = Mock(return_value=conn)
        mock_get_conn.return_value.__exit__ = Mock(return_value=False)
        
        cursor.fetchall.return_value = []
        
        result = await get_ocr_confidence_distribution(current_user=mock_user)
        
        assert result["statistics"]["average"] == 0
        assert result["statistics"]["total"] == 0
    
    @pytest.mark.asyncio
    @patch('app.api.analytics.db_manager.get_connection')
    async def test_get_ocr_confidence_bins(self, mock_get_conn, mock_user, mock_db_connection):
        """Test OCR confidence score binning"""
        from app.api.analytics import get_ocr_confidence_distribution
        
        conn, cursor = mock_db_connection
        mock_get_conn.return_value.__enter__ = Mock(return_value=conn)
        mock_get_conn.return_value.__exit__ = Mock(return_value=False)
        
        cursor.fetchall.return_value = [
            (0.3,),   # low
            (0.6,),   # medium
            (0.8,),   # good
            (0.9,),   # very_good
            (0.97,)   # excellent
        ]
        
        result = await get_ocr_confidence_distribution(current_user=mock_user)
        
        assert result["distribution"]["low"] == 1
        assert result["distribution"]["medium"] == 1
        assert result["distribution"]["good"] == 1
        assert result["distribution"]["very_good"] == 1
        assert result["distribution"]["excellent"] == 1
    
    @pytest.mark.asyncio
    @patch('app.api.analytics.db_manager.get_connection')
    async def test_get_chat_distribution_by_day(self, mock_get_conn, mock_user, mock_db_connection):
        """Test chat distribution by day"""
        from app.api.analytics import get_chat_distribution_by_day
        
        conn, cursor = mock_db_connection
        mock_get_conn.return_value.__enter__ = Mock(return_value=conn)
        mock_get_conn.return_value.__exit__ = Mock(return_value=False)
        
        cursor.fetchall.return_value = [
            (datetime(2024, 1, 1).date(), 10),
            (datetime(2024, 1, 2).date(), 15),
            (datetime(2024, 1, 3).date(), 8)
        ]
        
        result = await get_chat_distribution_by_day(current_user=mock_user)
        
        assert "daily_data" in result
        assert "statistics" in result
        assert len(result["daily_data"]) == 3
        assert result["statistics"]["total"] == 33
        assert result["statistics"]["max"] == 15
        assert result["statistics"]["min"] == 8
    
    @pytest.mark.asyncio
    @patch('app.api.analytics.db_manager.get_connection')
    async def test_get_chat_distribution_empty(self, mock_get_conn, mock_user, mock_db_connection):
        """Test chat distribution with no data"""
        from app.api.analytics import get_chat_distribution_by_day
        
        conn, cursor = mock_db_connection
        mock_get_conn.return_value.__enter__ = Mock(return_value=conn)
        mock_get_conn.return_value.__exit__ = Mock(return_value=False)
        
        cursor.fetchall.return_value = []
        
        result = await get_chat_distribution_by_day(current_user=mock_user)
        
        assert result["statistics"]["total"] == 0
        assert result["statistics"]["average"] == 0
    
    @pytest.mark.asyncio
    @patch('app.api.analytics.db_manager.get_connection')
    async def test_database_error_handling(self, mock_get_conn, mock_user):
        """Test database error handling"""
        from app.api.analytics import get_document_uploads_over_time
        
        mock_get_conn.side_effect = Exception("Database connection failed")
        
        with pytest.raises(HTTPException) as exc_info:
            await get_document_uploads_over_time(period="7d", current_user=mock_user)
        
        assert exc_info.value.status_code == 500
    
    @pytest.mark.asyncio
    @patch('app.api.analytics.db_manager.get_connection')
    async def test_period_90d(self, mock_get_conn, mock_user, mock_db_connection):
        """Test 90 days period grouping"""
        from app.api.analytics import get_document_uploads_over_time
        
        conn, cursor = mock_db_connection
        mock_get_conn.return_value.__enter__ = Mock(return_value=conn)
        mock_get_conn.return_value.__exit__ = Mock(return_value=False)
        
        cursor.fetchall.side_effect = [
            [(datetime.now().date(), 20, 4096000)],
            [(100, 20480000, 204800, datetime.now(), datetime.now())]
        ]
        
        result = await get_document_uploads_over_time(period="90d", current_user=mock_user)
        
        assert result["period"] == "90d"
    
    @pytest.mark.asyncio
    @patch('app.api.analytics.db_manager.get_connection')
    async def test_period_1y(self, mock_get_conn, mock_user, mock_db_connection):
        """Test 1 year period grouping"""
        from app.api.analytics import get_document_uploads_over_time
        
        conn, cursor = mock_db_connection
        mock_get_conn.return_value.__enter__ = Mock(return_value=conn)
        mock_get_conn.return_value.__exit__ = Mock(return_value=False)
        
        cursor.fetchall.side_effect = [
            [(datetime.now().date(), 100, 20480000)],
            [(500, 102400000, 204800, datetime.now(), datetime.now())]
        ]
        
        result = await get_document_uploads_over_time(period="1y", current_user=mock_user)
        
        assert result["period"] == "1y"
    
    @pytest.mark.asyncio
    @patch('app.api.analytics.db_manager.get_connection')
    async def test_storage_usage_percentage_calculation(self, mock_get_conn, mock_user, mock_db_connection):
        """Test storage usage percentage calculation"""
        from app.api.analytics import get_storage_usage
        
        conn, cursor = mock_db_connection
        mock_get_conn.return_value.__enter__ = Mock(return_value=conn)
        mock_get_conn.return_value.__exit__ = Mock(return_value=False)
        
        total_storage = 300 * 1024 * 1024  # 300MB
        used_storage = 150 * 1024 * 1024   # 150MB (50%)
        cursor.fetchone.return_value = (used_storage,)
        
        result = await get_storage_usage(current_user=mock_user)
        
        assert abs(result["usagePercentage"] - 50.0) < 0.1
        assert result["availableStorage"] == total_storage - used_storage
