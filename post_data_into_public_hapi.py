import requests
import json

url = "http://hapi.fhir.org/baseR4/Questionnaire"
headers = {
    "Accept": "application/fhir+json;q=1.0, application/json+fhir;q=0.9",
    "Content-Type": "application/fhir+json; charset=UTF-8"
}
data = {
    "resourceType": "Questionnaire",
    "id": "example-questionnaire",
    "title": "Example Health Questionnaire",
    "status": "active",
    "subjectType": ["Patient"],
    "item": [
        {
            "linkId": "1",
            "text": "General Health Information",
            "type": "group",
            "item": [
                {
                    "linkId": "1.1",
                    "text": "What is your body temperature (in Celsius)?",
                    "type": "decimal"
                },
                {
                    "linkId": "1.2",
                    "text": "Which of the following symptoms have you experienced in the last week? (Select all that apply)",
                    "type": "choice",
                    "repeats": True,
                    "answerOption": [
                        {
                            "valueCoding": {
                                "code": "fever",
                                "display": "Fever"
                            },
                            "value": "Fever"
                        },
                        {
                            "valueCoding": {
                                "code": "cough",
                                "display": "Cough"
                            },
                            "value": "Cough"
                        }
                    ]
                }
            ]
        }
    ]
}

response = requests.post(url, headers=headers, data=json.dumps(data))
print("Status Code:", response.status_code)
print("Response:", response.json())
