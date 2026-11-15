"""
Rockfall Early Warning and Response Coordination System
Comprehensive Automated Test Suite

Tests:
1. Database integrity and seeded tables
2. Machine learning inference and XAI feature importance
3. Independent rule-based extreme reading detection
4. Emergency response protocol grounding & unverified safety fallback
5. All Flask web application routes and API endpoints
"""

import unittest
import json
import os
import sqlite3

from app import app
from database import get_db_connection
from prediction import predict_risk
from alert_system import evaluate_sensor_readings
from emergency_response import generate_grounded_evacuation_notice, get_zone_protocol


class TestRockfallSystem(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_01_database_tables_exist(self):
        """Verifies that all required SQLite tables exist and contain baseline records."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r['name'] for r in cursor.fetchall()]
        conn.close()

        required_tables = ['zones', 'sensor_readings', 'extreme_alerts', 'safety_protocols', 'threshold_configs', 'prediction_history']
        for table in required_tables:
            self.assertIn(table, tables, f"Missing database table: {table}")

    def test_02_ml_prediction_pipeline(self):
        """Verifies that the Supervised ML pipeline accurately classifies hazard levels."""
        # Test low risk sample
        low_sample = {
            'rainfall_mm': 10.0,
            'slope_angle_deg': 40.0,
            'vibration_intensity': 0.5,
            'soil_moisture_pct': 20.0,
            'displacement_rate_mm_day': 0.3,
            'rock_movement_mm': 0.8,
            'geological_condition': 'Stable Bedrock'
        }
        res_low = predict_risk(low_sample)
        self.assertIn('predicted_risk', res_low)
        self.assertIn('confidence_pct', res_low)
        self.assertIn('feature_contributions', res_low)
        self.assertEqual(res_low['predicted_risk'], 'Low Risk')

        # Test high risk sample
        high_sample = {
            'rainfall_mm': 180.0,
            'slope_angle_deg': 75.0,
            'vibration_intensity': 9.5,
            'soil_moisture_pct': 88.0,
            'displacement_rate_mm_day': 25.0,
            'rock_movement_mm': 38.0,
            'geological_condition': 'Loose Shale & Siltstone'
        }
        res_high = predict_risk(high_sample)
        self.assertEqual(res_high['predicted_risk'], 'High Risk')
        self.assertGreaterEqual(res_high['confidence_pct'], 70.0)

    def test_03_independent_rule_based_backstop(self):
        """Verifies that extreme readings trigger independent alerts even on benign inputs."""
        # Case where values are otherwise moderate, but vibration or displacement breaches critical limit
        spike_sample = {
            'rainfall_mm': 20.0,
            'slope_angle_deg': 45.0,
            'vibration_intensity': 12.5,  # Exceeds 9.0 critical limit
            'soil_moisture_pct': 30.0,
            'displacement_rate_mm_day': 1.0,
            'rock_movement_mm': 2.0,
            'geological_condition': 'Stable Bedrock'
        }
        rule_eval = evaluate_sensor_readings(spike_sample)
        self.assertTrue(rule_eval['has_alerts'])
        self.assertEqual(rule_eval['max_severity'], 'Critical')
        
        # Verify specific sensor responsible is highlighted
        sensor_keys = [a['sensor_key'] for a in rule_eval['alerts']]
        self.assertIn('vibration_intensity', sensor_keys)
        self.assertIn('danger_reason', rule_eval['alerts'][0])

    def test_04_emergency_protocol_grounding(self):
        """Verifies grounded protocol retrieval for Zone 1 and safety fallback for unverified zone."""
        # Zone 1 (North Ridge Pass) has a verified protocol
        zone1 = {'id': 1, 'name': 'North Ridge Pass', 'location': 'Sector 1', 'zone_code': 'ZONE-A'}
        notice_verified = generate_grounded_evacuation_notice(zone1, 'Displacement Spike')
        self.assertTrue(notice_verified['is_grounded'])
        self.assertIn('SOP-NR-2024-01', notice_verified['protocol_code'])
        self.assertIn('Service Access Track 1', notice_verified['evacuation_route'])

        # Zone 5 (Railway Tunnel Portal) has NO verified protocol
        zone5 = {'id': 5, 'name': 'Railway Tunnel Portal North', 'location': 'Sector 5', 'zone_code': 'ZONE-E'}
        notice_unverified = generate_grounded_evacuation_notice(zone5, 'Slope Failure')
        self.assertFalse(notice_unverified['is_grounded'])
        self.assertIn('safety_disclaimer', notice_unverified)
        self.assertIn('NEVER fabricates evacuation routes', notice_unverified['safety_disclaimer'])

    def test_05_web_routes(self):
        """Verifies that all 8 core web pages load with HTTP 200 OK."""
        routes = [
            '/',
            '/dashboard',
            '/prediction',
            '/monitoring',
            '/sensor-data',
            '/alerts',
            '/protocols',
            '/admin',
            '/about',
            '/chatbot',
            '/assistant'
        ]
        for route in routes:
            resp = self.app.get(route)
            self.assertEqual(resp.status_code, 200, f"Route {route} returned status {resp.status_code}")

    def test_06_api_endpoints(self):
        """Verifies JSON API response formats."""
        stats_resp = self.app.get('/api/stats')
        self.assertEqual(stats_resp.status_code, 200)
        data = json.loads(stats_resp.data)
        self.assertIn('total_zones', data)
        self.assertIn('low_risk_zones', data)

        predict_payload = {
            'rainfall_mm': 50.0,
            'slope_angle_deg': 55.0,
            'vibration_intensity': 2.0,
            'soil_moisture_pct': 40.0,
            'displacement_rate_mm_day': 3.0,
            'rock_movement_mm': 5.0,
            'geological_condition': 'Weathered Sandstone'
        }
        api_pred_resp = self.app.post('/api/predict', data=json.dumps(predict_payload), content_type='application/json')
        self.assertEqual(api_pred_resp.status_code, 200)
        pred_data = json.loads(api_pred_resp.data)
        self.assertTrue(pred_data['success'])
        self.assertIn('prediction', pred_data)
        self.assertIn('extreme_rules', pred_data)

    def test_07_rag_generative_response_synthesis(self):
        """Verifies RAG pipeline retrieval and confirmed AI-generated response synthesis."""
        from emergency_response import generate_rag_response

        # 1. Direct RAG function invocation for Zone 1
        query = "What is the emergency evacuation procedure for North Ridge Pass during heavy rainfall?"
        rag_res = generate_rag_response(query, zone_id=1, sensor_telemetry={'rainfall_mm': 120.0, 'vibration_intensity': 4.5})
        self.assertTrue(rag_res['success'])
        self.assertTrue(rag_res['is_grounded'])
        self.assertIn('ai_response', rag_res)
        self.assertIn('Service Access Track 1', rag_res['ai_response'])
        self.assertIn('97.8%', rag_res['grounding_confidence'])
        self.assertTrue(len(rag_res['grounding_evidence']) >= 3)

        # 2. REST API /api/rag/ask endpoint
        rag_api_resp = self.app.post(
            '/api/rag/ask',
            data=json.dumps({'query': 'Evacuation instructions for Highwall Zone A', 'zone_id': 1}),
            content_type='application/json'
        )
        self.assertEqual(rag_api_resp.status_code, 200)
        rag_api_data = json.loads(rag_api_resp.data)
        self.assertTrue(rag_api_data['success'])
        self.assertIn('ai_response', rag_api_data)

        # 3. Web UI POST /protocols
        post_resp = self.app.post('/protocols', data={'rag_query': 'Sector 1 emergency protocol', 'zone_id': '1'})
        self.assertEqual(post_resp.status_code, 200)
        self.assertIn(b'RAG AI Safety Copilot', post_resp.data)


if __name__ == '__main__':
    unittest.main()
