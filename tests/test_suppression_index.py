import pytest
from datetime import datetime, timedelta
from rabbitmirror.suppression_index import SuppressionIndex


@pytest.fixture
def sample_entries():
    """Sample entries for suppression analysis."""
    base_time = datetime.now() - timedelta(days=60)
    return [
        {'timestamp': (base_time + timedelta(days=i)).isoformat(), 'category': 'news'}
        for i in range(15)
    ] + [
        {'timestamp': (base_time + timedelta(days=i, hours=1)).isoformat(), 'category': 'entertainment'}
        for i in range(15, 30)
    ] + [
        {'timestamp': (base_time + timedelta(days=i, hours=2)).isoformat(), 'category': 'news'}
        for i in range(30, 45)
    ] + [
        {'timestamp': (base_time + timedelta(days=i, hours=3)).isoformat(), 'category': 'entertainment'}
        for i in range(45, 60)
    ]


class TestSuppressionIndex:
    """Test suite for the SuppressionIndex class."""
    
    def test_initialization(self):
        """Test SuppressionIndex initialization."""
        si = SuppressionIndex(baseline_period_days=30)
        assert si.baseline_period_days == 30
    
    def test_calculate_suppression(self, sample_entries):
        """Test basic suppression calculation."""
        si = SuppressionIndex(baseline_period_days=30)
        results = si.calculate_suppression(sample_entries)
        
        assert 'overall_suppression' in results
        assert 'category_suppression' in results
        assert 'temporal_patterns' in results
        
        # Check specific results (mocked logic)
        assert isinstance(results['overall_suppression'], float)
        assert isinstance(results['category_suppression'], dict)
        assert 'news' in results['category_suppression']
        assert 'entertainment' in results['category_suppression']
    
    def test_find_split_point(self, sample_entries):
        """Test finding split point for baseline and analysis periods."""
        si = SuppressionIndex(baseline_period_days=30)
        split_point = si._find_split_point(sample_entries)
        assert split_point == len(sample_entries) // 2
    
    def test_calculate_period_metrics(self, sample_entries):
        """Test calculation of period metrics."""
        si = SuppressionIndex(baseline_period_days=30)
        metrics = si._calculate_period_metrics(sample_entries)
        
        assert 'total_views' in metrics
        assert 'unique_channels' in metrics
        assert 'category_distribution' in metrics
        assert 'view_velocity' in metrics
        
        assert metrics['total_views'] == len(sample_entries)
        assert isinstance(metrics['view_velocity'], float)
    
    def test_get_category_distribution(self, sample_entries):
        """Test category distribution calculation."""
        si = SuppressionIndex(baseline_period_days=30)
        distribution = si._get_category_distribution(sample_entries)
        
        assert isinstance(distribution, dict)
        assert len(distribution) > 0
        
        # Check that probabilities sum to 1
        total_prob = sum(distribution.values())
        assert abs(total_prob - 1.0) < 0.001
        
        # Check specific categories exist
        assert 'news' in distribution
        assert 'entertainment' in distribution

    def test_view_velocity_calculation(self, sample_entries):
        """Test view velocity calculation."""
        si = SuppressionIndex(baseline_period_days=30)
        velocity = si._calculate_view_velocity(sample_entries)
        
        assert isinstance(velocity, float)
        assert velocity > 0
    
    def test_overall_suppression_calculation(self, sample_entries):
        """Test overall suppression calculation logic."""
        si = SuppressionIndex(baseline_period_days=30)
        baseline_metrics = si._calculate_period_metrics(sample_entries[:30])
        analysis_metrics = si._calculate_period_metrics(sample_entries[30:])
        
        suppression = si._calculate_overall_suppression(baseline_metrics, analysis_metrics)
        
        assert isinstance(suppression, float)
        assert 0 <= suppression <= 1
    
    def test_category_suppression_calculation(self, sample_entries):
        """Test category-specific suppression calculation logic."""
        si = SuppressionIndex(baseline_period_days=30)
        baseline_metrics = si._calculate_period_metrics(sample_entries[:30])
        analysis_metrics = si._calculate_period_metrics(sample_entries[30:])
        
        category_suppression = si._calculate_category_suppression(baseline_metrics, analysis_metrics)
        
        assert isinstance(category_suppression, dict)
        for category, suppression in category_suppression.items():
            assert 0 <= suppression <= 1
    
    def test_empty_entries(self):
        """Test suppression calculation with empty entries."""
        si = SuppressionIndex(baseline_period_days=30)
        results = si.calculate_suppression([])
        
        assert 'overall_suppression' in results
        assert 'category_suppression' in results
        assert 'temporal_patterns' in results
    
    def test_zero_baseline_views(self):
        """Test suppression calculation when baseline has zero views."""
        si = SuppressionIndex(baseline_period_days=30)
        
        baseline_metrics = {'total_views': 0, 'category_distribution': {}}
        analysis_metrics = {'total_views': 10, 'category_distribution': {'news': 1.0}}
        
        suppression = si._calculate_overall_suppression(baseline_metrics, analysis_metrics)
        assert suppression == 0.0
