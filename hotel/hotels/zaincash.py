import uuid
import requests

import base64
import hashlib
import hmac
import json
import time

from django.conf import settings



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






















def inquiry_payment(transaction_id):
    """
    Check the current status of a ZainCash transaction.
    """

    if not transaction_id:
        raise ValueError("Missing ZainCash transaction ID")

    access_token = get_access_token()

    url = (
        f"{ZAINCASH_BASE_URL}"
        f"/api/v2/payment-gateway/transaction/inquiry/{transaction_id}"
    )

    response = requests.get(
        url,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        timeout=30,
    )

    print("ZainCash inquiry status:", response.status_code)
    print("ZainCash inquiry response:", response.text)

    response.raise_for_status()

    return response.json()




def verify_zaincash_callback_token(token):
    """
    Verify ZainCash redirect JWT.

    ZainCash callback tokens are signed using:
        HS256

    The secret must be the API Secret Key provided by ZainCash.
    """

    if not token:
        raise ValueError("Missing ZainCash callback token")

    try:
        # JWT must contain exactly 3 parts
        parts = token.split(".")

        if len(parts) != 3:
            raise ValueError("Invalid JWT format")

        encoded_header = parts[0]
        encoded_payload = parts[1]
        encoded_signature = parts[2]

        # -------------------------------------------------
        # Decode header
        # -------------------------------------------------

        def base64url_decode(value):
            padding = "=" * (-len(value) % 4)
            return base64.urlsafe_b64decode(
                value + padding
            )

        header = json.loads(
            base64url_decode(encoded_header)
        )

        payload = json.loads(
            base64url_decode(encoded_payload)
        )

        # -------------------------------------------------
        # Verify algorithm
        # -------------------------------------------------

        if header.get("alg") != "HS256":
            raise ValueError(
                "Invalid JWT algorithm"
            )

        # -------------------------------------------------
        # Get ZainCash API Secret
        # -------------------------------------------------

        secret = getattr(
            settings,
            "ZAINCASH_API_SECRET",
            None
        )

        if not secret:
            raise ValueError(
                "ZAINCASH_API_SECRET is not configured"
            )

        # -------------------------------------------------
        # Verify signature
        # -------------------------------------------------

        signing_input = (
            encoded_header
            + "."
            + encoded_payload
        ).encode("utf-8")

        expected_signature = hmac.new(
            secret.encode("utf-8"),
            signing_input,
            hashlib.sha256
        ).digest()

        received_signature = base64url_decode(
            encoded_signature
        )

        if not hmac.compare_digest(
            expected_signature,
            received_signature
        ):
            raise ValueError(
                "Invalid ZainCash token signature"
            )

        # -------------------------------------------------
        # Verify expiration
        # -------------------------------------------------

        exp = payload.get("exp")

        if exp is not None:

            if time.time() >= float(exp):
                raise ValueError(
                    "ZainCash token has expired"
                )

        # -------------------------------------------------
        # Verify not-before if present
        # -------------------------------------------------

        nbf = payload.get("nbf")

        if nbf is not None:

            if time.time() < float(nbf):
                raise ValueError(
                    "ZainCash token is not active yet"
                )

        return payload

    except ValueError:
        raise

    except Exception as e:

        raise ValueError(
            "Invalid ZainCash callback token"
        ) from e