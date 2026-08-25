import uuid
import requests

from django.conf import settings


ZAINCASH_BASE_URL = "https://pg-api-uat.zaincash.iq"


def get_access_token():
    url = f"{ZAINCASH_BASE_URL}/oauth2/token"

    data = {
        "grant_type": "client_credentials",
        "client_id": settings.ZAINCASH_CLIENT_ID,
        "client_secret": settings.ZAINCASH_CLIENT_SECRET,
        "scope": "payment:read payment:write",
    }

    response = requests.post(
        url,
        data=data,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
        },
        timeout=30,
    )

    response.raise_for_status()

    return response.json()["access_token"]


def create_payment(
    booking_id,
    amount,
    success_url,
    failure_url,
    customer_phone=None,
):
    access_token = get_access_token()

    url = (
        f"{ZAINCASH_BASE_URL}"
        "/api/v2/payment-gateway/transaction/init"
    )

    # New unique ID for every payment attempt
    external_reference_id = str(uuid.uuid4())

    payload = {
        "language": "en",

        "externalReferenceId": external_reference_id,

        "orderId": str(booking_id),

        "serviceType": "Hotel Booking",

        "amount": {
            "value": str(int(round(amount))),
            "currency": "IQD",
        },

        "redirectUrls": {
            "successUrl": success_url,
            "failureUrl": failure_url,
        },
    }

    if customer_phone:
        payload["customer"] = {
            "phone": customer_phone,
        }

    response = requests.post(
        url,
        json=payload,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        timeout=30,
    )

    # Useful for debugging ZainCash errors
    print("ZainCash status:", response.status_code)
    print("ZainCash response:", response.text)

    response.raise_for_status()

    return response.json()