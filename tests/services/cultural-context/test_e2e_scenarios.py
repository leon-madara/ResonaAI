"""
End-to-End Test Scenarios for Cultural Context Service
Tests complete user journeys and real-world scenarios
"""

import pytest
import json
from fastapi.testclient import TestClient

# Import the cultural context app
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "apps", "backend", "services", "cultural-context"))

from main import app


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Authentication headers"""
    return {"Authorization": "Bearer test-token"}


class TestRealWorldScenarios:
    """Test real-world user scenarios"""
    
    def test_scenario_young_adult_academic_pressure(self, client, auth_headers):
        """
        Scenario: Young adult struggling with academic pressure
        User: 22-year-old university student who failed exams
        """
        # Turn 1: Initial contact - minimizing
        response1 = client.post(
            "/cultural-analysis",
            json={
                "text": "Ni sawa tu, ni shule tu",
                "language": "sw",
                "emotion": "neutral"
            },
            headers=auth_headers
        )
        assert response1.status_code == 200
        data1 = response1.json()
        
        # Should detect minimization
        assert data1["cultural_context"]["deflection_analysis"]["deflection_detected"] is True
        
        # Turn 2: Opens up about failure
        response2 = client.post(
            "/cultural-analysis",
            json={
                "text": "Nimeshindwa mitihani, familia wangu watakuwa na aibu",
                "language": "sw",
                "emotion": "sad"
            },
            headers=auth_headers
        )
        assert response2.status_code == 200
        data2 = response2.json()
        
        # Should retrieve context about academic failure and family shame
        context_text = " ".join([
            entry.get("content", "")
            for entry in data2["cultural_context"]["cultural_context"]
        ]).lower()
        
        assert any(keyword in context_text for keyword in [
            "academic", "education", "failure", "shame", "family", "pressure"
        ])
        
        # Turn 3: Expresses hopelessness
        response3 = client.post(
            "/cultural-analysis",
            json={
                "text": "Sina sababu ya kuendelea, nimeshindwa",
                "language": "sw",
                "emotion": "hopeless"
            },
            headers=auth_headers
        )
        assert response3.status_code == 200
        data3 = response3.json()
        
        # Should detect hopelessness and provide crisis support
        deflections = data3["cultural_context"]["deflection_analysis"]["deflections"]
        hopeless_patterns = [d for d in deflections if "hopeless" in d.get("type", "").lower()]
        assert len(hopeless_patterns) > 0
    
    def test_scenario_mother_postpartum_depression(self, client, auth_headers):
        """
        Scenario: New mother experiencing postpartum depression
        User: 28-year-old woman, 3 months postpartum
        """
        # Turn 1: Expresses exhaustion
        response1 = client.post(
            "/cultural-analysis",
            json={
                "text": "Nimechoka sana na watoto wangu",
                "language": "sw",
                "emotion": "tired"
            },
            headers=auth_headers
        )
        assert response1.status_code == 200
        data1 = response1.json()
        
        # Should detect parental stress pattern
        deflections = data1["cultural_context"]["deflection_analysis"]["deflections"]
        parental_patterns = [d for d in deflections if "watoto" in d.get("pattern", "").lower()]
        assert len(parental_patterns) > 0
        
        # Turn 2: Mentions inability to feel joy
        response2 = client.post(
            "/cultural-analysis",
            json={
                "text": "Sifurahi na mtoto wangu, familia wanasema ni aibu",
                "language": "sw",
                "emotion": "sad"
            },
            headers=auth_headers
        )
        assert response2.status_code == 200
        data2 = response2.json()
        
        # Should retrieve context about postpartum depression and stigma
        context_text = " ".join([
            entry.get("content", "")
            for entry in data2["cultural_context"]["cultural_context"]
        ]).lower()
        
        assert any(keyword in context_text for keyword in [
            "postpartum", "motherhood", "childbirth", "maternal"
        ])
        
        # Should provide privacy-focused guidance
        assert "privacy" in data2["conversation_guidance"]
    
    def test_scenario_man_hiding_depression(self, client, auth_headers):
        """
        Scenario: Man hiding depression due to masculinity norms
        User: 35-year-old man, unemployed, feeling worthless
        """
        # Turn 1: Deflects with work stress
        response1 = client.post(
            "/cultural-analysis",
            json={
                "text": "Ni kazi tu, pesa ni shida",
                "language": "sw",
                "emotion": "neutral"
            },
            headers=auth_headers
        )
        assert response1.status_code == 200
        data1 = response1.json()
        
        # Should detect work/financial stress deflection
        deflections = data1["cultural_context"]["deflection_analysis"]["deflections"]
        work_patterns = [d for d in deflections if "kazi" in d.get("pattern", "").lower() or "pesa" in d.get("pattern", "").lower()]
        assert len(work_patterns) > 0
        
        # Turn 2: Expresses feeling powerless
        response2 = client.post(
            "/cultural-analysis",
            json={
                "text": "Sina nguvu, siwezi kusaidia familia yangu",
                "language": "sw",
                "emotion": "sad"
            },
            headers=auth_headers
        )
        assert response2.status_code == 200
        data2 = response2.json()
        
        # Should detect powerlessness pattern
        deflections2 = data2["cultural_context"]["deflection_analysis"]["deflections"]
        powerless_patterns = [d for d in deflections2 if "nguvu" in d.get("pattern", "").lower()]
        assert len(powerless_patterns) > 0
        
        # Should retrieve context about male mental health and provider stress
        context_text = " ".join([
            entry.get("content", "")
            for entry in data2["cultural_context"]["cultural_context"]
        ]).lower()
        
        assert any(keyword in context_text for keyword in [
            "men", "male", "masculinity", "provider", "financial"
        ])
    
    def test_scenario_domestic_violence_survivor(self, client, auth_headers):
        """
        Scenario: Woman experiencing domestic violence
        User: 30-year-old woman in abusive marriage
        """
        # Turn 1: Mentions marriage problems indirectly
        response1 = client.post(
            "/cultural-analysis",
            json={
                "text": "Ndoa yangu ni ngumu, lakini familia wanasema nivumilie",
                "language": "sw",
                "emotion": "sad"
            },
            headers=auth_headers
        )
        assert response1.status_code == 200
        data1 = response1.json()
        
        # Should detect marriage stress pattern
        deflections = data1["cultural_context"]["deflection_analysis"]["deflections"]
        marriage_patterns = [d for d in deflections if "ndoa" in d.get("pattern", "").lower()]
        assert len(marriage_patterns) > 0
        
        # Should retrieve context about domestic violence and cultural barriers
        context_text = " ".join([
            entry.get("content", "")
            for entry in data1["cultural_context"]["cultural_context"]
        ]).lower()
        
        assert any(keyword in context_text for keyword in [
            "domestic", "violence", "abuse", "marriage", "relationship"
        ])
        
        # Should provide privacy-focused guidance
        assert "privacy" in data1["conversation_guidance"]
        
        # Turn 2: Expresses fear
        response2 = client.post(
            "/cultural-analysis",
            json={
                "text": "Naogopa, lakini sina mahali pa kwenda",
                "language": "sw",
                "emotion": "fearful"
            },
            headers=auth_headers
        )
        assert response2.status_code == 200
        data2 = response2.json()
        
        # Should detect fear pattern
        deflections2 = data2["cultural_context"]["deflection_analysis"]["deflections"]
        fear_patterns = [d for d in deflections2 if "ogopa" in d.get("pattern", "").lower()]
        assert len(fear_patterns) > 0
        
        # Should have elevated risk level
        assert data2["overall_risk_level"] in ["medium", "high"]
    
    def test_scenario_lgbtq_hiding_identity(self, client, auth_headers):
        """
        Scenario: LGBTQ+ individual hiding identity
        User: 24-year-old person struggling with identity and family rejection
        """
        # Turn 1: Expresses family misunderstanding
        response1 = client.post(
            "/cultural-analysis",
            json={
                "text": "Familia yangu hawanielewi, wanasema ni aibu",
                "language": "sw",
                "emotion": "sad"
            },
            headers=auth_headers
        )
        assert response1.status_code == 200
        data1 = response1.json()
        
        # Should detect family misunderstanding pattern
        deflections = data1["cultural_context"]["deflection_analysis"]["deflections"]
        family_patterns = [d for d in deflections if "familia" in d.get("pattern", "").lower()]
        assert len(family_patterns) > 0
        
        # Turn 2: Expresses isolation
        response2 = client.post(
            "/cultural-analysis",
            json={
                "text": "Sina marafiki, nina upweke sana",
                "language": "sw",
                "emotion": "lonely"
            },
            headers=auth_headers
        )
        assert response2.status_code == 200
        data2 = response2.json()
        
        # Should detect isolation pattern
        deflections2 = data2["cultural_context"]["deflection_analysis"]["deflections"]
        isolation_patterns = [d for d in deflections2 if "marafiki" in d.get("pattern", "").lower() or "upweke" in d.get("pattern", "").lower()]
        assert len(isolation_patterns) > 0
        
        # Should have elevated risk level due to isolation
        assert data2["overall_risk_level"] in ["medium", "high"]
    
    def test_scenario_elder_caregiver_burnout(self, client, auth_headers):
        """
        Scenario: Adult child caring for elderly parent
        User: 45-year-old woman caring for mother with dementia
        """
        # Turn 1: Expresses exhaustion
        response1 = client.post(
            "/cultural-analysis",
            json={
                "text": "Nimechoka kuchunguza mama yangu, lakini ni wajibu wangu",
                "language": "sw",
                "emotion": "tired"
            },
            headers=auth_headers
        )
        assert response1.status_code == 200
        data1 = response1.json()
        
        # Should detect exhaustion pattern
        deflections = data1["cultural_context"]["deflection_analysis"]["deflections"]
        exhaustion_patterns = [d for d in deflections if "choka" in d.get("pattern", "").lower()]
        assert len(exhaustion_patterns) > 0
        
        # Should retrieve context about caregiver burden
        context_text = " ".join([
            entry.get("content", "")
            for entry in data1["cultural_context"]["cultural_context"]
        ]).lower()
        
        assert any(keyword in context_text for keyword in [
            "caregiver", "elder", "care", "burden", "duty"
        ])
        
        # Turn 2: Expresses guilt about feelings
        response2 = client.post(
            "/cultural-analysis",
            json={
                "text": "Naomba radhi kwa kuhisi hivi, ni dhambi",
                "language": "sw",
                "emotion": "guilty"
            },
            headers=auth_headers
        )
        assert response2.status_code == 200
        data2 = response2.json()
        
        # Should detect excessive apologizing
        deflections2 = data2["cultural_context"]["deflection_analysis"]["deflections"]
        apology_patterns = [d for d in deflections2 if "omba radhi" in d.get("pattern", "").lower()]
        assert len(apology_patterns) > 0


class TestCulturallySpecificScenarios:
    """Test culturally specific scenarios"""
    
    def test_scenario_witchcraft_attribution(self, client, auth_headers):
        """
        Scenario: Mental health symptoms attributed to witchcraft
        User: Family believes symptoms are caused by curse
        """
        response = client.post(
            "/cultural-analysis",
            json={
                "text": "Familia wanasema ni uchawi, wameenda kwa mganga",
                "language": "sw",
                "emotion": "confused"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should retrieve context about spiritual attribution
        context_text = " ".join([
            entry.get("content", "")
            for entry in data["cultural_context"]["cultural_context"]
        ]).lower()
        
        assert any(keyword in context_text for keyword in [
            "witchcraft", "spiritual", "traditional", "curse", "belief"
        ])
        
        # Should provide spirituality-focused guidance
        assert "spirituality" in data["conversation_guidance"]
    
    def test_scenario_polygamy_stress(self, client, auth_headers):
        """
        Scenario: Woman in polygamous marriage experiencing jealousy
        User: Second wife dealing with co-wife competition
        """
        response = client.post(
            "/cultural-analysis",
            json={
                "text": "Mke mwingine wa mume wangu ananichukia, nina wasiwasi",
                "language": "sw",
                "emotion": "anxious"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should retrieve context about polygamy and relationship dynamics
        context_text = " ".join([
            entry.get("content", "")
            for entry in data["cultural_context"]["cultural_context"]
        ]).lower()
        
        assert any(keyword in context_text for keyword in [
            "polygamy", "co-wife", "wives", "marriage", "jealousy"
        ])
    
    def test_scenario_infertility_stigma(self, client, auth_headers):
        """
        Scenario: Woman facing infertility stigma
        User: Unable to conceive, facing family pressure
        """
        response = client.post(
            "/cultural-analysis",
            json={
                "text": "Sina watoto, familia ya mume wanasema ni laana",
                "language": "sw",
                "emotion": "sad"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should retrieve context about infertility stigma
        context_text = " ".join([
            entry.get("content", "")
            for entry in data["cultural_context"]["cultural_context"]
        ]).lower()
        
        assert any(keyword in context_text for keyword in [
            "infertility", "childless", "reproductive", "stigma"
        ])
        
        # Should provide privacy-focused guidance
        assert "privacy" in data["conversation_guidance"]
    
    def test_scenario_hiv_stigma(self, client, auth_headers):
        """
        Scenario: Person living with HIV facing stigma
        User: Recently diagnosed, afraid of disclosure
        """
        response = client.post(
            "/cultural-analysis",
            json={
                "text": "Nina ugonjwa, naogopa watu wajue, watanicheka",
                "language": "sw",
                "emotion": "fearful"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should detect fear pattern
        deflections = data["cultural_context"]["deflection_analysis"]["deflections"]
        fear_patterns = [d for d in deflections if "ogopa" in d.get("pattern", "").lower()]
        assert len(fear_patterns) > 0
        
        # Should retrieve context about health-related stigma
        context_text = " ".join([
            entry.get("content", "")
            for entry in data["cultural_context"]["cultural_context"]
        ]).lower()
        
        # May retrieve HIV stigma or general health stigma context
        assert any(keyword in context_text for keyword in [
            "hiv", "stigma", "discrimination", "health", "disclosure"
        ])


class TestPerformanceAndReliability:
    """Test performance and reliability"""
    
    def test_service_handles_rapid_requests(self, client, auth_headers):
        """Test service can handle rapid successive requests"""
        messages = [
            "Nimechoka",
            "Sawa tu",
            "Sina nguvu",
            "Familia yangu",
            "Nataka kusema"
        ]
        
        for message in messages:
            response = client.post(
                "/cultural-analysis",
                json={
                    "text": message,
                    "language": "sw",
                    "emotion": "neutral"
                },
                headers=auth_headers
            )
            assert response.status_code == 200
            assert "cultural_context" in response.json()
    
    def test_service_handles_long_text(self, client, auth_headers):
        """Test service can handle long text input"""
        long_text = " ".join([
            "Nimechoka sana na maisha yangu.",
            "Familia yangu hawanielewi.",
            "Nina wasiwasi kuhusu kazi na pesa.",
            "Watoto wangu wanahitaji mengi.",
            "Sina nguvu ya kuendelea.",
            "Naomba radhi kwa kusumbua."
        ] * 5)  # Repeat 5 times
        
        response = client.post(
            "/cultural-analysis",
            json={
                "text": long_text,
                "language": "sw",
                "emotion": "sad"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should detect multiple patterns
        deflections = data["cultural_context"]["deflection_analysis"]["deflections"]
        assert len(deflections) > 0
    
    def test_service_handles_mixed_languages(self, client, auth_headers):
        """Test service handles mixed language input"""
        mixed_texts = [
            "I am feeling nimechoka and wasiwasi",
            "My familia doesn't understand, wanasema ni aibu",
            "Sina nguvu but I have to keep going",
            "Nataka kusema something important"
        ]
        
        for text in mixed_texts:
            response = client.post(
                "/cultural-analysis",
                json={
                    "text": text,
                    "language": "en",
                    "emotion": "neutral"
                },
                headers=auth_headers
            )
            assert response.status_code == 200
            assert "cultural_context" in response.json()
    
    def test_service_handles_special_characters(self, client, auth_headers):
        """Test service handles special characters and punctuation"""
        texts_with_special_chars = [
            "Nimechoka!!! Sana!!!",
            "Sawa... tu...",
            "Sina nguvu???",
            "Familia yangu... (sigh)"
        ]
        
        for text in texts_with_special_chars:
            response = client.post(
                "/cultural-analysis",
                json={
                    "text": text,
                    "language": "sw",
                    "emotion": "neutral"
                },
                headers=auth_headers
            )
            assert response.status_code == 200
            assert "cultural_context" in response.json()


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_text_handling(self, client, auth_headers):
        """Test handling of empty text"""
        response = client.post(
            "/cultural-analysis",
            json={
                "text": "",
                "language": "sw",
                "emotion": "neutral"
            },
            headers=auth_headers
        )
        # Should either handle gracefully or return appropriate error
        assert response.status_code in [200, 400]
    
    def test_very_short_text(self, client, auth_headers):
        """Test handling of very short text"""
        short_texts = ["Hi", "Ok", "No", "Yes"]
        
        for text in short_texts:
            response = client.post(
                "/cultural-analysis",
                json={
                    "text": text,
                    "language": "en",
                    "emotion": "neutral"
                },
                headers=auth_headers
            )
            assert response.status_code == 200
    
    def test_unknown_language(self, client, auth_headers):
        """Test handling of unknown language"""
        response = client.post(
            "/cultural-analysis",
            json={
                "text": "Some text",
                "language": "unknown",
                "emotion": "neutral"
            },
            headers=auth_headers
        )
        # Should handle gracefully
        assert response.status_code == 200
    
    def test_missing_optional_fields(self, client, auth_headers):
        """Test handling of missing optional fields"""
        response = client.post(
            "/cultural-analysis",
            json={
                "text": "Nimechoka sana"
                # Missing language and emotion
            },
            headers=auth_headers
        )
        # Should handle with defaults
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
