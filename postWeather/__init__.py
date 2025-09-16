import logging
import azure.functions as func
import json

app = func.FunctionApp()

# Décorateur : Function Name + Trigger + Binding de sortie vers CosmosDB
@app.function_name(name="postWeather")
@app.route(route="postWeather", methods=["POST"], auth_level=func.AuthLevel.ANONYMOUS)
@app.cosmos_db_output(
    arg_name="outputDocument",
    connection="COSMOS_CONN_STRING",   # défini dans local.settings.json ou App Settings Azure
    database_name="weatherdb",
    container_name="temperatures",
    create_if_not_exists=True
)
def post_weather(req: func.HttpRequest, outputDocument: func.Out[func.Document]) -> func.HttpResponse:
    logging.info("Processing POST /postWeather")

    try:
        # Lire le JSON envoyé dans la requête
        body = req.get_json()
        date = body.get("date")
        avg_temp = body.get("avg_temp")

        if not date or avg_temp is None:
            return func.HttpResponse(
                json.dumps({"error": "Missing required fields: date, avg_temp"}),
                mimetype="application/json",
                status_code=400
            )

        # Créer le document JSON
        document = {
            "id": date,         # ID unique = la date (clé primaire)
            "date": date,
            "avg_temp": avg_temp
        }

        # Écrire dans Cosmos DB
        outputDocument.set(func.Document.from_dict(document))

        return func.HttpResponse(
            json.dumps({"status": "saved", "document": document}),
            mimetype="application/json",
            status_code=201
        )

    except Exception as e:
        logging.error(f"Erreur lors de l’insertion : {e}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )

