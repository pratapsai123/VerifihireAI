"""
Razorpay Payment Integration for Student AI Credits.

Flow:
1. Frontend calls POST /api/students/payment/create-order/ with {amount: 200} (in INR)
2. Backend creates a Razorpay order and returns order_id + key_id
3. Frontend opens Razorpay checkout popup with the order_id
4. On success, frontend calls POST /api/students/payment/verify/ with payment details
5. Backend verifies signature, credits the wallet, logs the transaction
"""
import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

logger = logging.getLogger(__name__)

CREDITS_PER_RUPEE = 3


def _get_razorpay_client():
    """Lazy-initialize Razorpay client."""
    import razorpay
    from decouple import config
    key_id = config('RAZORPAY_KEY_ID', default='')
    key_secret = config('RAZORPAY_KEY_SECRET', default='')
    return razorpay.Client(auth=(key_id, key_secret))


def _get_razorpay_key_id():
    """Get the Razorpay key ID for frontend."""
    from decouple import config
    return config('RAZORPAY_KEY_ID', default='')


class CreatePaymentOrderView(APIView):
    """
    POST /api/students/payment/create-order/
    Creates a Razorpay order for the given amount (INR).
    Returns: { order_id, amount, currency, key_id }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not hasattr(request.user, 'profile'):
            return Response({"error": "Profile not found."}, status=status.HTTP_403_FORBIDDEN)

        amount = request.data.get('amount')
        try:
            amount = int(amount)
        except (TypeError, ValueError):
            return Response({"error": "Invalid amount."}, status=status.HTTP_400_BAD_REQUEST)

        if amount < 1 or amount > 10000:
            return Response({"error": "Amount must be between ₹1 and ₹10,000."}, status=status.HTTP_400_BAD_REQUEST)

        # Amount in paise (Razorpay expects smallest currency unit)
        amount_paise = amount * 100

        try:
            client = _get_razorpay_client()
            order_data = {
                "amount": amount_paise,
                "currency": "INR",
                "receipt": f"credits_{request.user.id}_{amount}",
                "notes": {
                    "user_id": str(request.user.id),
                    "email": request.user.email,
                    "credits": str(amount * CREDITS_PER_RUPEE),
                }
            }
            order = client.order.create(data=order_data)

            return Response({
                "order_id": order["id"],
                "amount": amount,
                "amount_paise": amount_paise,
                "currency": "INR",
                "key_id": _get_razorpay_key_id(),
                "credits_to_add": amount * CREDITS_PER_RUPEE,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Razorpay order creation failed: {e}")
            return Response({
                "error": "Payment service unavailable. Please try again later.",
                "detail": str(e),
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class VerifyPaymentView(APIView):
    """
    POST /api/students/payment/verify/
    Verifies Razorpay payment signature and credits the wallet.
    Expects: { razorpay_order_id, razorpay_payment_id, razorpay_signature, amount }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not hasattr(request.user, 'profile'):
            return Response({"error": "Profile not found."}, status=status.HTTP_403_FORBIDDEN)

        razorpay_order_id = request.data.get('razorpay_order_id')
        razorpay_payment_id = request.data.get('razorpay_payment_id')
        razorpay_signature = request.data.get('razorpay_signature')
        amount = request.data.get('amount')

        if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature, amount]):
            return Response({"error": "Missing payment verification fields."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = int(amount)
        except (TypeError, ValueError):
            return Response({"error": "Invalid amount."}, status=status.HTTP_400_BAD_REQUEST)

        # Verify signature
        try:
            client = _get_razorpay_client()
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            client.utility.verify_payment_signature(params_dict)
        except Exception as e:
            logger.warning(f"Payment signature verification failed: {e}")
            return Response({
                "error": "Payment verification failed. Signature mismatch.",
            }, status=status.HTTP_400_BAD_REQUEST)

        # Signature valid — credit the wallet
        credits_to_add = amount * CREDITS_PER_RUPEE
        profile = request.user.profile
        profile.ai_credits = (profile.ai_credits or 0) + credits_to_add
        profile.save(update_fields=['ai_credits'])

        # Log the transaction
        from api.models import CreditTransaction
        CreditTransaction.objects.create(
            user_profile=profile,
            transaction_type=CreditTransaction.TYPE_ADDED,
            amount=credits_to_add,
            balance_after=profile.ai_credits,
            description=f"Razorpay ₹{amount} (Payment: {razorpay_payment_id[:12]}...)",
        )

        return Response({
            "message": f"Payment verified! Added {credits_to_add} AI credits.",
            "credits_added": credits_to_add,
            "ai_credits": profile.ai_credits,
            "payment_id": razorpay_payment_id,
        }, status=status.HTTP_200_OK)
