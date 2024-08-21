from gpt_function_decorator import gpt_function


def test_ai_healthcare_example():
    @docgpt
    def predict_disease_risk(age: int, gender: str, symptoms: str):
        """Predict the risk of a disease based on age, gender, and symptoms.
        
        Parameters:
        - age: Age of the patient
        - gender: Gender of the patient
        - symptoms: Symptoms described by the patient
        """

    result = predict_disease_risk(age=30, gender="Male", symptoms="Fever, cough")
    assert "risk" in result.lower()
