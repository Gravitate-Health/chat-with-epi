import json
from flask import render_template, request, jsonify
from chat_app import app
import requests
from chat_app.core import FHIR_IPS_URL, FHIR_EPI_URL, process_bundle, process_ips, medicationchat
import markdown


print(app.config)


@app.route("/", methods=["GET"])
def hello():
    return render_template("chat.html")

@app.route("/chat/<bundleid>", methods=["POST"])
def lens_app(bundleid=None):
    epibundle = None
    ips = None

    patientIdentifier = request.args.get("patientIdentifier", "")
    model = request.args.get("model", "llama3")  # defautl
    question = request.args.get("question", None)

    data = request.json
    epibundle = data.get("epi")
    ips = data.get("ips")
    question = data.get("question")

    # print(epibundle)
    if ips is None and patientIdentifier == "":
        return "Error: missing IPS", 404
    # preprocessed_bundle, ips = separate_data(bundleid, patientIdentifier)
    if epibundle is None and bundleid is None:
        return "Error: missing EPI", 404
    if question is None:
        return "Error: missing Question", 404
    if epibundle is None:
        print("epibundle is none")
        # print(epibundle)
        # print(bundleid)
        print(FHIR_EPI_URL + "/Bundle/" + bundleid)
        epibundle = requests.get(FHIR_EPI_URL + "/Bundle/" + bundleid).json()
    # print(epibundle)
    language, epi, drug_name = process_bundle(epibundle)

    if ips is None:
        payload = json.dumps({
            "resourceType" : "Parameters",
            "id" : "Focusing IPS request",
            "parameter" : [{
                "name" : "identifier",
                "valueIdentifier" : {"value": patientIdentifier}
            }]
        })
        headers = {
            "Content-Type": "application/json"
        }
        ips_url = FHIR_IPS_URL + "/Patient/$summary"
        response = requests.request("POST", ips_url, headers=headers, data=payload)
        ips = response.json()
    gender, age, diagnostics, medications = process_ips(ips)

    # Return the JSON response
    chated = medicationchat(
        language, drug_name, gender, age, diagnostics, medications, question, epi, model
    )
    return markdown.markdown(chated["response"])
