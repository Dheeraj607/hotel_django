import json

from django.core.serializers import serialize

from hotel_app.serializers import RoomSerializer, BookingSerializer, PaymentSerializer, RoomSimpleDetailSerializer, \
    ExtraServiceSerializer, RefundSerializer, MultiRoleControlSerializer, PaymentCheckoutSerializer, \
    CustomerListSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from hotel_app.models import Rooms, Booking, Payment, Customer, ExtraService, Refund, MultiRoleController, \
    ExtraServiceCategory, User


@api_view(['GET'])
def rooms_available(request):
    rooms = Rooms.objects.all()
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Rooms, Booking, Payment
from .serializers import BookingSerializer, PaymentSerializer

from datetime import datetime
import pytz

from datetime import datetime
import pytz
from rest_framework.response import Response
from rest_framework.decorators import api_view

from datetime import datetime
import pytz
from rest_framework.response import Response
from rest_framework.decorators import api_view
import os
from django.core.files.storage import default_storage
from datetime import datetime
import pytz
from rest_framework.response import Response
from rest_framework.decorators import api_view
import os
import json
from django.core.files.storage import default_storage
from .models import Rooms, User, ImageProof
from .serializers import BookingSerializer


# @api_view(['POST'])
# def book_room_and_payment(request):
#     room_id = request.data.get('roomId')
#     if not room_id:
#         return Response({"error": "roomId is required."}, status=400)
#
#     try:
#         room = Rooms.objects.get(roomId=room_id)
#     except Rooms.DoesNotExist:
#         return Response({"error": "Room not found."}, status=404)
#
#     if room.status.strip().lower() not in ["available", "unoccupied"]:
#         return Response({"error": "Room is not available."}, status=400)
#
#     check_in_time_str = request.data.get('checkInTime')
#     if not check_in_time_str:
#         return Response({"error": "checkInTime is required."}, status=400)
#
#     try:
#         check_in_time = datetime.strptime(check_in_time_str, "%I:%M %p")
#         india_tz = pytz.timezone('Asia/Kolkata')
#         check_in_time = india_tz.localize(check_in_time)
#     except ValueError:
#         return Response({"error": "Invalid checkInTime format."}, status=400)
#
#     # Prepare booking data
#     input_data = request.data.copy()
#     user = User.objects.filter(userId=2).first()
#     createdBy = user.pk
#     updatedBy = user.pk
#
#     # Convert customer_input and payment from JSON strings to dicts if present
#     customer_input = input_data.get("customer_input")
#     if customer_input:
#         customer_input = json.loads(customer_input)
#         customer_input["createdBy"] = createdBy
#         customer_input["updatedBy"] = updatedBy
#         input_data["customer_input"] = customer_input
#
#     payment_input = input_data.get("payment")
#     if payment_input:
#         payment_input = json.loads(payment_input)
#         payment_input["createdBy"] = createdBy
#         payment_input["updatedBy"] = updatedBy
#         input_data["payment"] = payment_input
#
#     input_data["createdBy"] = createdBy
#     input_data["updatedBy"] = updatedBy
#
#     # Use the serializer to create a booking instance
#     import pdb;pdb.set_trace()
#     serializer = BookingSerializer(data=input_data)
#     if serializer.is_valid():
#         booking = serializer.save()
#
#         # Update room status to "Occupied"
#         room.status = "Occupied"
#         room.save()
#
#         response_data = serializer.data
#
#         # Handle ImageProof upload if photos are provided
#         photos = request.FILES.getlist('photos')
#         if photos:
#             photo_paths = []
#             for photo in photos:
#                 path = default_storage.save(os.path.join('uploads', photo.name), photo)
#                 photo_paths.append(path)
#
#             proof_name = request.data.get('proofName', 'ID Proof')
#             image_proof = ImageProof.objects.create(
#                 customer_id=booking.customerId,
#                 name=proof_name,
#                 photos=photo_paths
#             )
#
#             # Include ImageProof data in response
#             response_data['image_proof_id'] = image_proof.id
#             response_data['image_proof_photos'] = photo_paths
#         else:
#             return Response({"error": "Please upload at least one photo."}, status=400)
#
#         return Response(response_data, status=201)
#     else:
#         return Response(serializer.errors, status=400)


# @api_view(['POST'])
# def book_room_and_payment(request):
#     room_id = request.data.get('roomId')
#     if not room_id:
#         return Response({"error": "roomId is required."}, status=400)
#
#     try:
#         room = Rooms.objects.get(roomId=room_id)
#     except Rooms.DoesNotExist:
#         return Response({"error": "Room not found."}, status=404)
#
#     # Check if the room is available (allow "available" or "unoccupied")
#     if room.status.strip().lower() not in ["available", "unoccupied"]:
#         return Response({"error": "Room is not available."}, status=400)
#
#     # Extract check-in time from the request
#     check_in_time_str = request.data.get('checkInTime')
#     if not check_in_time_str:
#         return Response({"error": "checkInTime is required."}, status=400)
#
#     try:
#         # Parse checkInTime in 12-hour format with AM/PM
#         check_in_time = datetime.strptime(check_in_time_str, "%I:%M %p")
#         # Assuming the time is in UTC, convert to IST
#         india_tz = pytz.timezone('Asia/Kolkata')
#         check_in_time = india_tz.localize(check_in_time)
#     except ValueError:
#         return Response({"error": "Invalid checkInTime format."}, status=400)
#
#     # Serialize the booking data
#     input_data = request.data
#     user = User.objects.filter(userId=2).first()
#     createdBy = user.pk
#     updatedBy = user.pk
#     input_data["createdBy"] = createdBy
#     input_data["updatedBy"] = updatedBy
#     input_data["customer_input"]["createdBy"] = createdBy
#     input_data["customer_input"]["updatedBy"] = updatedBy
#     input_data["payment"]["createdBy"] = createdBy
#     input_data["payment"]["updatedBy"] = updatedBy
#     # print("input_data  >> \n", input_data)
#     serializer = BookingSerializer(data=input_data)
#     if serializer.is_valid():
#         booking = serializer.save()
#
#         # Update room status to "Occupied" after successful booking
#         room.status = "Occupied"
#         room.save()
#
#         # Prepare payment data with checkInTime
#         # payment_data = request.data.get('payment', {})
#         # payment_data['bookingId'] = booking.bookingId  # Link payment to the created booking
#         # payment_data['paymentRemarks'] = payment_data.get('paymentRemarks', 'Check-in Advance')
#         # # Create the payment object with the provided data
#         # Payment.objects.create(**payment_data)
#
#         return Response(serializer.data, status=201)
#     else:
#         return Response(serializer.errors, status=400)


@api_view(['POST'])
def book_room_and_payment(request):
    room_id = request.data.get('roomId')
    if not room_id:
        return Response({"error": "roomId is required."}, status=400)

    try:
        room = Rooms.objects.get(roomId=room_id)
    except Rooms.DoesNotExist:
        return Response({"error": "Room not found."}, status=404)

    # Check if the room is available (allow "available" or "unoccupied")
    if room.status.strip().lower() not in ["available", "unoccupied"]:
        return Response({"error": "Room is not available."}, status=400)

    # Extract check-in time from the request
    check_in_time_str = request.data.get('checkInTime')
    if not check_in_time_str:
        return Response({"error": "checkInTime is required."}, status=400)

    # Prepare booking data
    input_data = request.data
    user = User.objects.filter(userId=2).first()  # Assume user is found, replace as needed
    createdBy = user
    updatedBy = user

    input_data["createdBy"] = createdBy.pk
    input_data["updatedBy"] = updatedBy.pk

    # Handle customer input
    customer_input = input_data.get("customer_input")
    # import pdb; pdb.set_trace()
    if customer_input:
        customer_input = json.loads(customer_input)
        customer_input["createdBy"] = createdBy
        customer_input["updatedBy"] = updatedBy
        input_data["customer_input"] = customer_input

        # Create or get the customer object
        customer, created = Customer.objects.get_or_create(
            idPassportNumber=customer_input.get("idPassportNumber"),
            defaults=customer_input
        )

        input_data["customerId"] = customer.customerId  # Link the customer to the booking
    else:
        customer = None
    # Handle payment input
    payment_input = input_data.get("payment")
    if payment_input:
        payment_input = json.loads(payment_input)
        payment_input["createdBy"] = user
        payment_input["updatedBy"] = user
        input_data["payment"] = payment_input

    # Now serialize the booking data
    # import pdb;pdb.set_trace()
    serializer = BookingSerializer(data=input_data)
    if serializer.is_valid():
        booking = serializer.save()

        # Create Payment object
        payment_data = input_data.get("payment", {})
        payment_data['bookingId'] = booking.bookingId  # Link payment to the created booking
        payment_data['paymentRemarks'] = payment_data.get('paymentRemarks', 'Check-in Advance')
        booking.customerId = customer.customerId
        booking.save()
        # Create the payment object with the provided data
        payment = Payment.objects.create(**payment_data)

        # Update room status to "Occupied" after successful booking
        room.status = "Occupied"
        room.save()

        # Handle ImageProof upload
        try:
            customer_id = customer.customerId
        except Exception as e:
            return Response({"error": str(e)}, 500)
        photos = request.FILES.getlist('photos')

        if photos:
            photo_paths = []
            for photo in photos:
                path = default_storage.save(os.path.join('uploads', photo.name), photo)
                photo_paths.append(path)

            proof_name = request.data.get('proofName', 'ID Proof')
            image_proof = ImageProof.objects.create(
                customer_id=customer_id,
                name=proof_name,
                photos=photo_paths
            )

            # Include ImageProof in response
            response_data = serializer.data
            response_data['image_proof_id'] = image_proof.id
            response_data['image_proof_photos'] = photo_paths
        else:
            response_data = serializer.data

        # Return the full response with customerId and payment data
        response_data['customerId'] = customer_id
        response_data['paymentId'] = payment.paymentId
        return Response(response_data, status=201)
    else:
        return Response(serializer.errors, status=400)


#
# @api_view(['POST'])
# def book_room_and_payment(request):
#     room_id = request.data.get('roomId')
#     if not room_id:
#         return Response({"error": "roomId is required."}, status=400)
#
#     try:
#         room = Rooms.objects.get(roomId=room_id)
#     except Rooms.DoesNotExist:
#         return Response({"error": "Room not found."}, status=404)
#
#     # Check if the room is available (allow "available" or "unoccupied")
#     if room.status.strip().lower() not in ["available", "unoccupied"]:
#         return Response({"error": "Room is not available."}, status=400)
#
#     # input_data = request.data.copy()
#     # user = User.objects.filter(userId=2).first()  # Assume user is found, replace as needed
#     # createdBy = user
#     # updatedBy = user
#     #
#     # input_data["createdBy"] = createdBy.pk
#     # input_data["updatedBy"] = updatedBy.pk
#
#     # customer_input = input_data.get("customer_input")
#     # import pdb;
#     # pdb.set_trace()
#     # if customer_input:
#     #     customer_input = json.loads(customer_input)
#     #     customer_input["createdBy"] = createdBy
#     #     customer_input["updatedBy"] = updatedBy
#     #     input_data["customer_input"] = customer_input
#     #
#     # # Handle payment input
#     # payment_input = input_data.get("payment")
#     # if payment_input:
#     #     payment_input = json.loads(payment_input)
#     #     payment_input["createdBy"] = user
#     #     payment_input["updatedBy"] = user
#     #     input_data["payment"] = payment_input
#
#     # Proceed with serializer
#
#     input_data = request.data.copy()
#     user = User.objects.filter(userId=2).first()
#     input_data["createdBy"] = user.pk
#     input_data["updatedBy"] = user.pk
#
#     # ✅ Manually load customer_input JSON string into a dict
#     customer_input_str = input_data.get("customer_input")
#     if customer_input_str:
#         customer_input = json.loads(customer_input_str)
#         customer_input["createdBy"] = user
#         customer_input["updatedBy"] = user
#         input_data.setlist("customer_input", [customer_input])  # force it as list of dict (DRF expects nested dict)
#
#     # ✅ Manually load payment JSON string
#     payment_input_str = input_data.get("payment")
#     if payment_input_str:
#         payment_input = json.loads(payment_input_str)
#         payment_input["createdBy"] = user
#         payment_input["updatedBy"] = user
#         input_data.setlist("payment", [payment_input])
#
#
#     import pdb;pdb.set_trace()
#     serializer = BookingSerializer(data=input_data)
#     if serializer.is_valid():
#         booking = serializer.save()
#
#         # After saving, mark the room as occupied
#         room.status = "Occupied"
#         room.save()
#
#         # Handle image proof upload
#         customer_id = booking.customerId
#         photos = request.FILES.getlist('photos')
#
#         if photos:
#             photo_paths = []
#             for photo in photos:
#                 path = default_storage.save(os.path.join('uploads', photo.name), photo)
#                 photo_paths.append(path)
#
#             proof_name = request.data.get('proofName', 'ID Proof')
#             image_proof = ImageProof.objects.create(
#                 customer_id=customer_id,
#                 name=proof_name,
#                 photos=photo_paths
#             )
#
#             # Include ImageProof in response
#             response_data = BookingSerializer(booking).data
#             response_data['image_proof_id'] = image_proof.id
#             response_data['image_proof_photos'] = photo_paths
#         else:
#             response_data = BookingSerializer(booking).data
#
#         return Response(response_data, status=201)
#     else:
#         return Response(serializer.errors, status=400)





from rest_framework.decorators import api_view
from rest_framework.response import Response
from hotel_app.models import Booking, Customer, Payment, Rooms
from hotel_app.serializers import BookingSerializer, CustomerSerializer, PaymentSerializer


@api_view(["PUT"])
def update_booking(request, booking_id):
    """Handles updating an existing booking, including customer and payment details."""
    try:
        booking = Booking.objects.get(bookingId=booking_id)
    except Booking.DoesNotExist:
        return Response({"error": "Booking not found"}, status=404)

    # user = User.objects.filter(userId=request.user.pk).first()
    user = User.objects.filter(userId=2).first()
    updatedBy = user.pk
    updatedAt = datetime.now()
    # ✅ Extract nested customer and payment data separately
    customer_data = request.data.pop("customer_input", None)
    customer_data["updatedBy"] = updatedBy
    customer_data["updatedAt"] = updatedAt
    payment_data = request.data.pop("payment", None)
    payment_data["updatedBy"] = updatedBy
    # payment_data["updatedAt"] = updatedAt

    # ✅ Update customer details if provided
    if customer_data:
        customer = Customer.objects.filter(idPassportNumber=customer_data.get("idPassportNumber")).first()
        if customer:
            for attr, value in customer_data.items():
                setattr(customer, attr, value)
            customer.save()
        else:
            customer = Customer.objects.create(**customer_data)

        request.data["customerId"] = customer.customerId

    # ✅ Update the booking itself
    serializer = BookingSerializer(booking, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()

        # ✅ Update payment details if provided
        if payment_data:
            Payment.objects.update_or_create(
                bookingId=booking.bookingId,
                defaults=payment_data
            )

        return Response(
            {"message": "Booking updated successfully"},  # ✅ Return only a message
            status=200
        )

    return Response(serializer.errors, status=400)


@api_view(['GET'])
def payment_detail(request, booking_id):
    payments = Payment.objects.filter(bookingId=booking_id)  # Fetch all payments for the given bookingId
    if payments.exists():
        return Response({
            "message": "Payments found",
            "data": PaymentSerializer(payments, many=True).data  # Use many=True to serialize multiple payments
        })
    else:
        return Response({"error": "No payments found for this bookingId"}, status=404)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q
from datetime import datetime
from .models import Rooms, Booking, Customer, Payment
from .serializers import RoomSimpleDetailSerializer


@api_view(['GET'])
def all_room_details(request):
    # Start with all rooms.
    rooms_qs = Rooms.objects.all()

    # -- ROOM-LEVEL FILTERS --
    room_id = request.GET.get('roomId', '').strip()
    room_number = request.GET.get('roomNumber', '').strip()
    room_type = request.GET.get('roomType', '').strip()
    status_filter = request.GET.get('status', '').strip()

    if room_id:
        try:
            rooms_qs = rooms_qs.filter(roomId=int(room_id))
        except ValueError:
            return Response({"error": "Invalid roomId format."}, status=400)
    if room_number:
        rooms_qs = rooms_qs.filter(roomNumber__icontains=room_number)
    if room_type:
        rooms_qs = rooms_qs.filter(roomType__icontains=room_type)
    if status_filter:
        rooms_qs = rooms_qs.filter(status__iexact=status_filter)

    # -- BOOKING-LEVEL FILTERS --
    from_date = request.GET.get('from_date', '').strip()
    to_date = request.GET.get('to_date', '').strip()
    name = request.GET.get('name', '').strip()
    payment_status = request.GET.get('payment_status', '').strip()

    # Build a booking queryset using the booking-level filters.
    booking_qs = Booking.objects.all()
    if from_date:
        booking_qs = booking_qs.filter(checkInDate__gte=from_date)
    if to_date:
        booking_qs = booking_qs.filter(checkInDate__lte=to_date)
    if name:
        customer_ids = list(
            Customer.objects.filter(fullName__iexact=name).values_list('customerId', flat=True)
        )
        booking_qs = booking_qs.filter(customerId__in=customer_ids) if customer_ids else Booking.objects.none()
    if payment_status:
        payment_booking_ids = list(
            Payment.objects.filter(paymentStatus__iexact=payment_status).values_list('bookingId', flat=True)
        )
        booking_qs = booking_qs.filter(
            bookingId__in=payment_booking_ids) if payment_booking_ids else Booking.objects.none()

    # If booking-level filters were applied, limit the rooms
    if from_date or to_date or name or payment_status:
        booking_room_ids = list(booking_qs.values_list('roomId', flat=True).distinct())
        rooms_qs = rooms_qs.filter(roomId__in=booking_room_ids)

    # Pass filter parameters to serializer context
    context = {
        'from_date': from_date,
        'to_date': to_date,
        'name': name,
        'payment_status': payment_status
    }

    serializer = RoomSimpleDetailSerializer(rooms_qs, many=True, context=context)
    return Response(serializer.data)


@api_view(['GET'])
def rooms(request):
    queryset = Rooms.objects.all()

    room_id = request.GET.get('roomId')
    room_number = request.GET.get('roomNumber')
    room_type = request.GET.get('roomType')
    status = request.GET.get('status')

    if room_id:
        try:
            room_id = int(room_id)
            queryset = queryset.filter(roomId=room_id)
        except ValueError:
            return Response({"error": "Invalid roomId format."}, status=400)

    if room_number:
        queryset = queryset.filter(roomNumber__iexact=room_number)

    if room_type:
        queryset = queryset.filter(roomType__iexact=room_type)

    if status:
        queryset = queryset.filter(status__iexact=status)

    serializer = RoomSerializer(queryset, many=True)
    return Response(serializer.data)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum
from .models import ExtraService, Payment
from .serializers import ExtraServiceSerializer, PaymentExtraInputSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum
from .models import ExtraService, Payment
from .serializers import ExtraServiceSerializer, PaymentExtraInputSerializer

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum
from .models import ExtraService, Payment
from .serializers import ExtraServiceSerializer, PaymentExtraInputSerializer


def update_payment_status(service_id):
    """ ✅ Updates ExtraService paymentStatus based on total payments made. """
    try:
        extra_service = ExtraService.objects.get(serviceId=service_id)
        total_paid = Payment.objects.filter(serviceId=service_id).aggregate(Sum('amount'))['amount__sum'] or 0

        if total_paid >= extra_service.serviceCost:
            extra_service.paymentStatus = "Paid"
        elif total_paid > 0:
            extra_service.paymentStatus = "Partially Paid"
        else:
            extra_service.paymentStatus = "Unpaid"

        extra_service.save()
    except ExtraService.DoesNotExist:
        pass  # Handle missing ExtraService gracefully


from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Booking, ExtraService, ExtraServiceCategory, Payment
from .serializers import ExtraServiceSerializer, PaymentExtraInputSerializer

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Booking, ExtraService, Payment, ExtraServiceCategory
from .serializers import ExtraServiceSerializer, PaymentExtraInputSerializer


@api_view(['POST'])
def create_payment_with_extras(request):
    print("Received Data:", request.data)
    booking_id = request.data.get("bookingId")
    extra_services_data = request.data.get("extraServices", [])

    if not booking_id:
        return Response({"error": "bookingId is required."}, status=400)

    try:
        booking = Booking.objects.get(bookingId=booking_id)
    except Booking.DoesNotExist:
        return Response({"error": f"Booking with ID {booking_id} not found."}, status=404)

    print("Booking Data:", booking)
    print("Extra Services Data:", extra_services_data)

    if not isinstance(extra_services_data, list) or not extra_services_data:
        return Response({"error": "extraServices must be a non-empty list."}, status=400)

    created_services = []
    input_data = request.data
    user = User.objects.filter(userId=2).first()
    createdBy = user.pk
    updatedBy = user.pk
    input_data["createdBy"] = createdBy
    input_data["updatedBy"] = updatedBy
    for extra_service_data in extra_services_data:
        service_cost = float(extra_service_data.get("serviceCost") or 0.0)
        payment_data = extra_service_data.pop("payment", None)

        extra_service_data["bookingId"] = booking.bookingId
        extra_service_data["createdBy"] = createdBy
        extra_service_data["updatedBy"] = updatedBy
        category_id = extra_service_data.get("categoryId", None)
        category = None

        if category_id:
            try:
                category = ExtraServiceCategory.objects.get(categoryId=category_id)
            except ExtraServiceCategory.DoesNotExist:
                return Response({"error": f"ExtraServiceCategory with categoryId {category_id} not found."}, status=404)

        if category:
            extra_service_data["categoryId"] = category.categoryId

        print(f"Assigned categoryId: {extra_service_data['categoryId']}")

        extra_service_serializer = ExtraServiceSerializer(data=extra_service_data)
        if extra_service_serializer.is_valid():
            extra_service = extra_service_serializer.save()
            total_paid = 0.0

            if payment_data:
                payment_data["serviceId"] = extra_service.serviceId
                payment_data["bookingId"] = booking.bookingId
                payment_data["paymentRemarks"] = "Extra Service"
                payment_data["createdBy"] = createdBy
                payment_data["updatedBy"] = updatedBy
                payment_serializer = PaymentExtraInputSerializer(data=payment_data)
                if payment_serializer.is_valid():
                    payment_instance = payment_serializer.save()
                    total_paid = float(payment_instance.amount or 0.0)
                else:
                    print("Payment Serializer Errors:", payment_serializer.errors)
                    return Response({"error": "Payment validation failed", "details": payment_serializer.errors},
                                    status=400)

            print(f"total_paid: {total_paid}, service_cost: {service_cost}")

            # ✅ Correct payment status based on total_paid
            if total_paid >= service_cost:
                payment_status = "Paid"
            elif total_paid > 0:
                payment_status = "Partially Paid"  # Corrected to match the choice in the model
            else:
                payment_status = "Unpaid"

            print(f"Calculated payment status: {payment_status}")

            extra_service.paymentStatus = payment_status
            extra_service.save()

            response_data = extra_service_serializer.data
            response_data["paymentStatus"] = payment_status

            created_services.append(response_data)
        else:
            return Response({"error": "Validation failed", "details": extra_service_serializer.errors}, status=400)

    return Response({
        "message": "Extra services and payments processed successfully!",
        "extraServices": created_services
    }, status=201)


@api_view(['GET'])
def get_all_extra_services(request):
    booking_id = request.query_params.get('bookingId')

    if not booking_id:
        return Response({"error": "bookingId query parameter is required."}, status=400)

    extra_services = ExtraService.objects.filter(bookingId=booking_id)

    if not extra_services.exists():
        return Response({"error": "No extra services found for this bookingId."}, status=404)

    serializer = ExtraServiceSerializer(extra_services, many=True)
    return Response(serializer.data, status=200)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum
from .models import ExtraService, Payment
from .serializers import PaymentExtraInputSerializer


@api_view(['POST'])
def add_payment_to_extra_service(request):
    """ ✅ Adds a payment and updates ExtraService payment status. """
    service_id = request.data.get("serviceId")
    payment_data = request.data.get("payment")

    if not service_id:
        return Response({"error": "serviceId is required."}, status=400)

    if not payment_data:
        return Response({"error": "Payment data is required."}, status=400)

    # ✅ Ensure `ExtraService` exists
    try:
        extra_service = ExtraService.objects.get(serviceId=service_id)
    except ExtraService.DoesNotExist:
        return Response({"error": "ExtraService not found."}, status=404)

    # ✅ Set serviceId for payment and ensure paymentStatus is always "Paid"
    payment_data["serviceId"] = service_id
    payment_data["paymentStatus"] = "Paid"

    # ✅ Save payment to database
    payment_serializer = PaymentExtraInputSerializer(data=payment_data)
    if payment_serializer.is_valid():
        payment_serializer.save()
    else:
        return Response(payment_serializer.errors, status=400)

    # ✅ Update ExtraService paymentStatus
    update_payment_status(service_id)

    return Response({"message": "Payment added successfully and ExtraService updated!"}, status=201)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import ExtraService, Payment
from .serializers import PaymentExtraInputSerializer
from datetime import datetime


@api_view(['PUT'])
def payment_for_service(request):
    print("Received data:", request.data)

    service_id = request.data.get("serviceId")
    amount = request.data.get("amount")
    payment_method = request.data.get("paymentMethod")
    transaction_id = request.data.get("transactionId")
    payment_type = request.data.get("paymentType")
    payment_date = request.data.get("paymentDate")

    # Validate the inputs
    if not service_id:
        return Response({"error": "serviceId is required."}, status=400)
    if not amount or amount <= 0:
        return Response({"error": "Valid amount is required."}, status=400)
    if not payment_date:
        return Response({"error": "paymentDate is required."}, status=400)

    try:
        # Retrieve the ExtraService object
        extra_service = ExtraService.objects.get(serviceId=service_id)
        user = User.objects.filter(userId=2).first()
        updatedBy = user.pk
        updatedAt = datetime.now()
        # Check if a payment already exists for this service
        existing_payment = Payment.objects.filter(serviceId=service_id).first()

        # If payment exists, update it, otherwise create a new one
        if existing_payment:
            # Update the existing payment record
            existing_payment.amount = amount
            existing_payment.paymentMethod = payment_method
            existing_payment.transactionId = transaction_id
            existing_payment.paymentType = payment_type
            existing_payment.paymentDate = payment_date
            existing_payment.paymentStatus = "Paid"  # Set as "Paid" when updating
            existing_payment.updatedBy = updatedBy
            existing_payment.updatedAt = updatedAt
            existing_payment.save()
        else:
            # If no payment exists, create a new payment entry
            payment_data = {
                "serviceId": service_id,
                "amount": amount,
                "paymentMethod": payment_method,
                "transactionId": transaction_id,
                "paymentStatus": "Paid",  # Set as "Paid" by default
                "paymentType": payment_type,
                "paymentDate": payment_date,
                "updatedBy": updatedBy,
                "updatedAt": updatedAt
            }
            payment_serializer = PaymentExtraInputSerializer(data=payment_data)

            if payment_serializer.is_valid():
                payment_serializer.save()
            else:
                return Response(payment_serializer.errors, status=400)

        # Update the payment status of the ExtraService object
        update_payment_status(service_id)

        return Response({"message": "Payment updated successfully!"}, status=200)

    except ExtraService.DoesNotExist:
        return Response({"error": "Service not found."}, status=404)


def update_payment_status(service_id):
    try:
        # Fetch the extra service by serviceId
        extra_service = ExtraService.objects.get(serviceId=service_id)

        # Check if the service has a payment associated
        if Payment.objects.filter(serviceId=service_id).exists():
            extra_service.paymentStatus = "Paid"
        else:
            extra_service.paymentStatus = "Pending"

        # Save the updated payment status
        extra_service.save()

    except ExtraService.DoesNotExist:
        pass  # Handle the case if serviceId doesn't exist


from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Refund
from .serializers import RefundSerializer


@api_view(['POST', 'GET', 'PUT'])
def refund_operations(request):
    from django.utils import timezone

    if request.method == 'POST':
        booking_id = request.data.get("bookingId")
        if not booking_id:
            return Response({"error": "bookingId is required."}, status=400)

        if not Booking.objects.filter(bookingId=booking_id).exists():
            return Response({"error": "bookingId not found."}, status=404)

        input_data = request.data.copy()

        # 👤 Simulate logged-in user (replace with request.user in real auth)
        user = User.objects.filter(userId=2).first()  # Or request.user
        if not user:
            return Response({"error": "User not found."}, status=400)

        user_id = user.pk
        now = timezone.now()

        # 🕓 Inject audit fields at top-level
        input_data["createdBy"] = user_id
        input_data["updatedBy"] = user_id
        input_data["createdAt"] = now
        input_data["updatedAt"] = now

        # ✅ Inject audit fields in nested `customer_input` if exists
        if "customer_input" in input_data:
            input_data["customer_input"]["createdBy"] = user_id
            input_data["customer_input"]["updatedBy"] = user_id
            input_data["customer_input"]["createdAt"] = now
            input_data["customer_input"]["updatedAt"] = now

        # ✅ Inject audit fields in nested `payment` if exists
        if "payment" in input_data:
            input_data["payment"]["createdBy"] = user_id
            input_data["payment"]["updatedBy"] = user_id
            input_data["payment"]["createdAt"] = now
            input_data["payment"]["updatedAt"] = now

        # 🔄 Now serialize and save
        serializer = RefundSerializer(data=input_data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Refund created successfully!", "data": serializer.data}, status=201)

        return Response(serializer.errors, status=400)

    elif request.method == 'GET':
        booking_id = request.query_params.get("bookingId")
        if not booking_id:
            return Response({"error": "bookingId is required for GET request."}, status=400)

        if not Booking.objects.filter(bookingId=booking_id).exists():
            return Response({"error": "Booking not found."}, status=404)

        refunds = Refund.objects.filter(bookingId=booking_id)
        if not refunds.exists():
            return Response({"error": "No refund found for this bookingId."}, status=404)

        serializer = RefundSerializer(refunds, many=True)
        return Response({"message": "Refund details retrieved successfully!", "data": serializer.data}, status=200)

    elif request.method == 'PUT':
        booking_id = request.data.get("bookingId")
        if not booking_id:
            return Response({"error": "bookingId is required for PUT request."}, status=400)

        if not Booking.objects.filter(bookingId=booking_id).exists():
            return Response({"error": "bookingId not found."}, status=404)

        refunds = Refund.objects.filter(bookingId=booking_id)
        if not refunds.exists():
            return Response({"error": "No refund found for this bookingId."}, status=404)

        user = User.objects.filter(userId=2).first()
        if not user:
            return Response({"error": "User with userId=2 not found."}, status=404)

        updated_by = user.pk
        updated_at = datetime.now()

        updated_refunds = []
        for refund in refunds:
            data = request.data.copy()  # Make a mutable copy for each refund
            data["updatedBy"] = updated_by
            data["updatedAt"] = updated_at

        updated_refunds = []
        for refund in refunds:
            serializer = RefundSerializer(refund, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                updated_refunds.append(serializer.data)
            else:
                return Response(serializer.errors, status=400)

        return Response({"message": "Refund(s) updated successfully!", "updated_data": updated_refunds}, status=200)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from hotel_app.models import RoomInspection, Payment
from hotel_app.serializers import (
    BookingInspectionSerializer,
    RoomInspectionSerializer,
    RoomInspectionInputSerializer,
    PaymentInputSerializer
)

from datetime import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import RoomInspection, Payment, User
from .serializers import BookingInspectionSerializer, PaymentInputSerializer


@api_view(['POST', 'GET', 'PUT'])
def room_inspection(request, *args, **kwargs):
    if request.method == 'POST':
        serializer = BookingInspectionSerializer(data=request.data)
        if serializer.is_valid():
            booking_id = serializer.validated_data['bookingId']
            inspections_data = serializer.validated_data['roomInspections']

            user = User.objects.filter(userId=2).first()  # Or use request.user with JWT
            created_by = updated_by = user
            updated_at = datetime.now()

            created_inspections = []
            for inspection_data in inspections_data:
                payment_data = inspection_data.pop('payment', None)

                # Add metadata to inspection
                inspection_data['createdBy'] = created_by
                inspection_data['updatedBy'] = updated_by
                inspection_data['updatedAt'] = updated_at

                # Create RoomInspection
                inspection = RoomInspection.objects.create(bookingId=booking_id, **inspection_data)

                # Handle Payment if provided
                payment_instance = None
                if payment_data and 'amount' in payment_data:
                    # Add booking and inspection references + metadata
                    payment_data['bookingId'] = booking_id
                    payment_data['inspectionId'] = inspection
                    payment_data['createdBy'] = created_by
                    payment_data['updatedBy'] = updated_by
                    payment_data['updatedAt'] = updated_at

                    # Create Payment instance
                    payment_instance = Payment.objects.create(**payment_data)

                # Append response data
                created_inspections.append({
                    "inspectionId": inspection.inspectionId,
                    "roomCondition": inspection.roomCondition,
                    "status": inspection.status,
                    "remarks": inspection.remarks,
                    "payment": PaymentInputSerializer(payment_instance).data if payment_instance else None
                })

            return Response({"bookingId": booking_id, "roomInspections": created_inspections}, status=201)

        return Response(serializer.errors, status=400)


    elif request.method == 'PUT':
        inspection_id = kwargs.get("inspection_id",None)
        booking_id = request.data.get("bookingId")
        inspections_data = request.data.get("roomInspections", [])
        if not inspections_data:
            return Response({"error": "No inspection data provided"}, status=400)
        user = User.objects.filter(userId=2).first()  # Or request.user with JWT
        updated_by = user
        updated_at = datetime.now()
        updated_inspections = []

        for inspection_data in inspections_data:
            if not inspection_id:
                return Response({"error": "inspectionId is required in roomInspections"}, status=400)
            try:
                inspection = RoomInspection.objects.get(inspectionId=inspection_id)
            except RoomInspection.DoesNotExist:
                return Response({"error": f"Inspection with ID {inspection_id} not found"}, status=404)

            # Add metadata
            inspection_data["updatedBy"] = updated_by.pk
            inspection_data["updatedAt"] = updated_at
            # Update inspection
            serializer = RoomInspectionInputSerializer(inspection, data=inspection_data, partial=True)
            if serializer.is_valid():
                updated_inspection = serializer.save()

                # Handle payment
                payment_data = inspection_data.get("payment")
                payment_instance = Payment.objects.filter(inspectionId=inspection).first()

                if payment_data:
                    payment_data["updatedBy"] = updated_by
                    payment_data["updatedAt"] = updated_at
                    if not payment_instance:
                        payment_instance = Payment.objects.create(
                            bookingId=inspection.bookingId,
                            inspectionId=inspection,
                            createdBy=updated_by,
                            **payment_data
                        )
                    else:
                        for key, value in payment_data.items():
                            setattr(payment_instance, key, value)
                        payment_instance.save()
                updated_inspections.append({
                    "inspectionId": updated_inspection.inspectionId,
                    "roomCondition": updated_inspection.roomCondition,
                    "status": updated_inspection.status,
                    "remarks": updated_inspection.remarks,
                    "payment": PaymentInputSerializer(payment_instance).data if payment_instance else None
                })
            else:
                return Response(serializer.errors, status=400)
        return Response({"bookingId": booking_id, "roomInspections": updated_inspections}, status=200)



    elif request.method == 'GET':
        inspection_id = kwargs.get("inspection_id", None)
        print(inspection_id)
        if not inspection_id:
            return Response({"error": "Inspection ID is required for fetching"}, status=400)

        try:
            inspection = RoomInspection.objects.get(inspectionId=inspection_id)
            payment_instance = Payment.objects.filter(inspectionId=inspection).first()

            return Response({
                "inspectionId": inspection.inspectionId,
                "roomCondition": inspection.roomCondition,
                "status": inspection.status,
                "remarks": inspection.remarks,
                "payment": PaymentInputSerializer(payment_instance).data if payment_instance else None
            }, status=200)

        except RoomInspection.DoesNotExist:
            return Response({"error": "Inspection not found"}, status=404)

    return Response({"error": "Invalid request method"}, status=405)


from rest_framework.decorators import api_view
from hotel_app.serializers import MaintenanceStaffRolesSerializer


# ✅ GET (all roles) & POST (create role)
@api_view(['GET', 'POST'])
def maintenance_roles_list(request):
    if request.method == 'GET':
        roles = MaintenanceStaffRoles.objects.all()
        serializer = MaintenanceStaffRolesSerializer(roles, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':

        input_data = request.data # Create a mutable copy of the input data

        user = User.objects.filter(userId=2).first()
        # if not user:
        #     return Response({"error": "User with userId=2 not found."}, status=404)
        createdBy = user.pk
        updatedBy = user.pk
        input_data["createdBy"] = createdBy
        input_data["updatedBy"] = updatedBy
        input_data["createdAt"] = datetime.now()
        input_data["updatedAt"] = datetime.now()

        serializer = MaintenanceStaffRolesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ✅ GET (single role) & PUT (update role)
@api_view(['GET', 'PUT'])
def maintenance_role_detail(request, role_id):
    try:
        role = MaintenanceStaffRoles.objects.get(roleId=role_id)
    except MaintenanceStaffRoles.DoesNotExist:
        return Response({"error": "Role not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = MaintenanceStaffRolesSerializer(role)
        return Response(serializer.data)

    elif request.method == 'PUT':

        input_data = request.data.copy()  # Make mutable copy
        user = User.objects.filter(userId=2).first()
        if not user:
            return Response({"error": "User with userId=2 not found."}, status=404)

        input_data["updatedBy"] = user.pk
        input_data["updatedAt"] = datetime.now()

        serializer = MaintenanceStaffRolesSerializer(role, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from hotel_app.models import MaintenanceStaff
from hotel_app.serializers import MaintenanceStaffSerializer, MaintenanceStaffNestedSerializer


# @api_view(['POST', 'GET'])
# def maintenance_staff_list(request):
#     if request.method == 'GET':
#         staff = MaintenanceStaff.objects.all()
#         serializer = MaintenanceStaffSerializer(staff, many=True)
#         return Response(serializer.data)
#
#     elif request.method == 'POST':
#         serializer = MaintenanceStaffSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST', 'GET'])
def maintenance_staff_list(request):
    if request.method == 'GET':
        staff_queryset = MaintenanceStaff.objects.select_related('staffId', 'roleId')

        # Apply filters
        role_id = request.GET.get('roleId')
        staff_id = request.GET.get('staffId')
        type_id = request.GET.get('typeId')

        if role_id:
            staff_queryset = staff_queryset.filter(roleId__roleId=role_id)
        if staff_id:
            staff_queryset = staff_queryset.filter(staffId__staffId=staff_id)
        if type_id:
            staff_queryset = staff_queryset.filter(roleId__typeId__typeId=type_id)

        # Group data by staffId
        grouped_data = {}

        for obj in staff_queryset:
            key = obj.staffId.staffId
            if key not in grouped_data:
                grouped_data[key] = {
                    "staffId": obj.staffId.staffId,
                    "staffName": obj.staffId.name,
                    "Roles": []
                }

            role = obj.roleId
            role_data = {
                "maintenanceStaffId": obj.id,
                "roleId": role.roleId,
                "roleName": role.roleName
            }

            if role_data not in grouped_data[key]["Roles"]:
                grouped_data[key]["Roles"].append(role_data)

        return Response(list(grouped_data.values()))



    elif request.method == 'POST':
        input_data = request.data
        user = User.objects.filter(userId=2).first()
        createdBy = user.pk
        updatedBy = user.pk
        input_data["createdBy"] = createdBy
        input_data["updatedBy"] = updatedBy
        input_data["createdAt"] = datetime.now()
        input_data["updatedAt"] = datetime.now()
        serializer = MaintenanceStaffSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
def maintenance_staff_detail(request, id):
    try:
        staff = MaintenanceStaff.objects.get(id=id)
    except MaintenanceStaff.DoesNotExist:
        return Response({"error": "Maintenance staff not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = MaintenanceStaffSerializer(staff)
        return Response(serializer.data)

    elif request.method == 'PUT':
        input_data = request.data.copy()  # Make mutable copy
        user = User.objects.filter(userId=2).first()
        if not user:
            return Response({"error": "User with userId=2 not found."}, status=404)

        input_data["updatedBy"] = user.pk
        input_data["updatedAt"] = datetime.now()

        serializer = MaintenanceStaffSerializer(staff, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from hotel_app.models import MaintenanceStaff, StaffManagement, MaintenanceRequest, MaintenanceAssignment
from hotel_app.serializers import MaintenanceRequestSerializer, MaintenanceAssignmentSerializer


from django.utils.timezone import now
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
def create_maintenance_request(request):
    """Handles creating a maintenance request and assigning it to a staff member."""

    # ✅ Required Fields Check
    required_fields = ["roomId", "issueDescription", "priorityLevel", "status", "requestDate"]
    missing_fields = [field for field in required_fields if field not in request.data]

    if missing_fields:
        return Response({"error": f"Missing required fields: {', '.join(missing_fields)}"},
                        status=status.HTTP_400_BAD_REQUEST)

    # ✅ Get user and time info
    user = User.objects.filter(userId=2).first()
    if not user:
        return Response({"error": "User with userId=2 not found."}, status=status.HTTP_404_NOT_FOUND)

    created_by = user.pk
    updated_by = user.pk


    # ✅ Inject audit fields into maintenance request data
    request_data = request.data.copy()
    request_data["createdBy"] = created_by
    request_data["updatedBy"] = updated_by
    request_data["createdAt"] = datetime.now()
    request_data["updatedAt"] = datetime.now()


    # ✅ Create Maintenance Request
    request_serializer = MaintenanceRequestSerializer(data=request_data)
    if not request_serializer.is_valid():
        return Response(request_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    maintenance_request = request_serializer.save()

    # ✅ Assign to Maintenance Staff if `maintenanceStaffId` is provided
    maintenance_staff_id = request.data.get("maintenanceStaffId")
    assignment_serializer = None

    if maintenance_staff_id:
        try:
            staff_instance = MaintenanceStaff.objects.get(id=maintenance_staff_id)
        except MaintenanceStaff.DoesNotExist:
            maintenance_request.delete()
            return Response({"error": f"Staff with ID {maintenance_staff_id} does not exist."},
                            status=status.HTTP_400_BAD_REQUEST)

        # ✅ Inject audit fields into assignment data
        assignment_data = {
            "requestId": maintenance_request.requestId,
            "maintenanceStaffId": staff_instance.id,
            "issueResolved": False,
            "comments": request.data.get("comments", ""),
            "createdBy": created_by,
            "updatedBy": updated_by,
            "createdAt": datetime.now()
,           "updatedAt": datetime.now()
,
        }

        assignment_serializer = MaintenanceAssignmentSerializer(data=assignment_data)
        if assignment_serializer.is_valid():
            assignment_serializer.save()
        else:
            maintenance_request.delete()
            return Response({
                "error": "Failed to save maintenance assignment",
                "details": assignment_serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    # ✅ Success Response
    return Response({
        "message": "Maintenance request and assignment saved successfully",
        "maintenanceRequest": request_serializer.data,
        "maintenanceAssignment": assignment_serializer.data if assignment_serializer else None
    }, status=status.HTTP_201_CREATED)

from rest_framework import generics
from .models import MaintenanceType
from .serializers import MaintenanceTypeSerializer


class MaintenanceTypeListView(generics.ListAPIView):
    queryset = MaintenanceType.objects.all()
    serializer_class = MaintenanceTypeSerializer




from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from .models import MaintenanceRequest, MaintenanceAssignment, MaintenanceType, MaintenanceStaff


@api_view(['GET'])
def get_maintenance_requests_with_staff(request):
    """Fetch maintenance requests with assigned staff details and filtering."""

    # Extract filter parameters
    request_id = request.GET.get('requestId')
    room_id = request.GET.get('roomId')
    maintenance_staff_id = request.GET.get('maintenanceStaffId')
    status_filter = request.GET.get('status')
    priority_level = request.GET.get('priorityLevel')
    role_id = request.GET.get('roleId')
    assigned_date = request.GET.get('assignedDate')
    issue_resolved = request.GET.get('issueResolved')

    # Start with all requests
    maintenance_requests = MaintenanceRequest.objects.all()

    # Filter by request data
    if request_id:
        maintenance_requests = maintenance_requests.filter(requestId=request_id)
    if room_id:
        maintenance_requests = maintenance_requests.filter(roomId=room_id)
    if status_filter:
        maintenance_requests = maintenance_requests.filter(status=status_filter)
    if priority_level:
        maintenance_requests = maintenance_requests.filter(priorityLevel=priority_level)

    response_data = []

    for request_obj in maintenance_requests:
        assignment = MaintenanceAssignment.objects.filter(requestId=request_obj).first()
        assignment_data = None
        typeId = request_obj.typeId.typeId
        typeName = request_obj.typeId.maintenanceTypeName
        if assignment:
            try:
                staff = assignment.maintenanceStaffId
                staff_member = staff.staffId if staff else None

                if not staff_member:
                    continue

                role_obj = staff_member.roleId if staff_member else None

                # ✅ Get the maintenance type directly from the request's typeId
                maintenance_type = "N/A"
                if request_obj.typeId:
                    maintenance_type = request_obj.typeId.maintenanceTypeName

                # Apply filters
                if maintenance_staff_id and str(staff.id) != maintenance_staff_id:
                    continue
                if role_id and (not role_obj or str(role_obj.roleId) != role_id):
                    continue
                if assigned_date and str(assignment.assignedDate.date()) != assigned_date:
                    continue
                if issue_resolved and str(assignment.issueResolved).lower() != issue_resolved.lower():
                    continue

                staff_details = {
                    "maintenanceStaffId": staff.id,
                    "maintenanceStaffName": staff_member.name,
                    "maintenanceStaffRole": role_obj.roleName if role_obj else "N/A",
                    "contactNumber": staff_member.contactNumber,
                    "maintenanceType": maintenance_type
                }

                assignment_data = {
                    "assignmentId": assignment.assignmentId,
                    "assignedDate": assignment.assignedDate,
                    "completionDate": assignment.completionDate,
                    "issueResolved": assignment.issueResolved,
                    "comments": assignment.comments,
                    "requestId": request_obj.requestId,
                    **staff_details
                }

            except ObjectDoesNotExist:
                continue
        # Final structure
        response_data.append({
            "requestId": request_obj.requestId,
            "roomId": request_obj.roomId,
            "issueDescription": request_obj.issueDescription,
            "priorityLevel": request_obj.priorityLevel,
            "requestDate": request_obj.requestDate,
            "status": request_obj.status,
            "maintenanceAssignment": assignment_data,
            "typeId": typeId,
            "typeName": typeName
        })

    return Response(response_data, status=status.HTTP_200_OK)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import MaintenanceRequest, MaintenanceAssignment, MaintenanceStaff
from django.shortcuts import get_object_or_404


@api_view(['PUT'])
def update_maintenance_request(request, requestId):
    """Handles PUT (update) a maintenance request or assignment using requestId in the URL."""

    # Ensure that requestId is passed and is valid
    if not requestId:
        return Response({"error": "requestId is required for updating."}, status=status.HTTP_400_BAD_REQUEST)

    # ✅ Get the Maintenance Request based on requestId from the URL
    maintenance_request = get_object_or_404(MaintenanceRequest, requestId=requestId)

    user = User.objects.filter(userId=2).first()
    if not user:
        return Response({"error": "User with userId=2 not found."}, status=status.HTTP_404_NOT_FOUND)

    updated_by = user.pk
    updated_at = datetime.now()

    # ✅ Update Maintenance Request fields if provided
    update_fields = []
    if 'status' in request.data:
        maintenance_request.status = request.data['status']
        update_fields.append('status')
    if 'priorityLevel' in request.data:
        maintenance_request.priorityLevel = request.data['priorityLevel']
        update_fields.append('priorityLevel')
    if 'issueDescription' in request.data:
        maintenance_request.issueDescription = request.data['issueDescription']
        update_fields.append('issueDescription')

    if update_fields:
        maintenance_request.updatedAt = updated_at
        maintenance_request.updatedBy_id = updated_by
        update_fields += ['updatedAt', 'updatedBy']
        maintenance_request.save(update_fields=update_fields)

    # ✅ Check if Maintenance Assignment needs an update
    assignment = MaintenanceAssignment.objects.filter(requestId=maintenance_request).first()
    if assignment:
        update_assignment_fields = []
        if 'assignedDate' in request.data:
            assignment.assignedDate = request.data['assignedDate']
            update_assignment_fields.append('assignedDate')
        if 'completionDate' in request.data:
            assignment.completionDate = request.data['completionDate']
            update_assignment_fields.append('completionDate')
        if 'issueResolved' in request.data:
            assignment.issueResolved = request.data['issueResolved']
            update_assignment_fields.append('issueResolved')
        if 'maintenanceStaffId' in request.data:
            try:
                new_staff = MaintenanceStaff.objects.get(id=request.data['maintenanceStaffId'])
                assignment.maintenanceStaffId = new_staff
                update_assignment_fields.append('maintenanceStaffId')
            except MaintenanceStaff.DoesNotExist:
                return Response({"error": "Invalid maintenanceStaffId."}, status=status.HTTP_400_BAD_REQUEST)

        if update_assignment_fields:
            assignment.updatedAt = updated_at
            assignment.updatedBy_id = updated_by
            update_assignment_fields += ['updatedAt', 'updatedBy']
            assignment.save(update_fields=update_assignment_fields)

    return Response({"message": "Maintenance request updated successfully."}, status=status.HTTP_200_OK)


@api_view(['POST'])
def add_roles(request):
    serializer = MultiRoleControlSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "user role added", "data": "inserted"}, status=status.HTTP_201_CREATED)
    else:
        return Response({"message": "failed", "error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_role_details(request, *args, **kwargs):
    staff_id = kwargs.get('id', None)  # This should be the staffManagement.staffId

    try:
        staff = StaffManagement.objects.get(staffId=staff_id)  # staffId is the actual PK
    except StaffManagement.DoesNotExist:
        return Response({"message": "Staff not found"}, status=status.HTTP_404_NOT_FOUND)

    roles = MaintenanceStaff.objects.filter(staffId=staff)  # This now filters correctly
    output = []

    for role in roles:
        role_dict = {
            'staffId': role.staffId.staffId,
            'staffName': role.staffId.name,
            'staffRole': role.roleId.roleName,
            'type': role.roleId.typeId.maintenanceTypeName
        }
        output.append(role_dict)

    return Response(output, status=status.HTTP_200_OK)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import MaintenanceType, MaintenanceStaffRoles, MaintenanceStaff


@api_view(['GET'])
def get_staff_by_type(request, *args, **kwargs):
    try:
        id = kwargs.get('id', None)

        # Step 1: Get the MaintenanceType
        maintenance_type = MaintenanceType.objects.get(typeId=id)

        # Step 2: Get all related roles for this MaintenanceType
        role_ids = MaintenanceStaffRoles.objects.filter(typeId=maintenance_type).values_list('roleId', flat=True)

        # Step 3: Get all staff with those roleIds
        staff_members = MaintenanceStaff.objects.select_related('staffId', 'roleId').filter(roleId__in=role_ids)

        # Step 4: Build output data
        output = []
        for entry in staff_members:
            staff = entry.staffId
            role = entry.roleId
            output.append({
                "maintenanceStaffId": entry.id,  # ✅ corrected here
                "staffId": staff.staffId,
                "name": staff.name,
                "email": staff.email,
                "contactNumber": staff.contactNumber,
                "address": staff.address,
                "roleId": role.roleId,
                "roleName": role.get_roleName_display(),
                "typeId": role.typeId.typeId,
                "typeName": role.typeId.get_maintenanceTypeName_display()
            })

        return Response(output, status=status.HTTP_200_OK)

    except MaintenanceType.DoesNotExist:
        return Response({"error": "Invalid typeId"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def modify_assignment(request):
    user = User.objects.filter(userId=2).first()
    if not user:
        return Response({"error": "User with userId=2 not found."}, status=status.HTTP_404_NOT_FOUND)

    created_by = user.pk
    updated_by = user.pk
    current_time = datetime.now()

    assignment_data = {
        "requestId": request.data.get('requestId', None),  # ✅ Link to Maintenance Request
        "maintenanceStaffId": request.data.get('staffId', None),  # ✅ Use maintenanceStaffId as FK
        "issueResolved": False,
        "comments": request.data.get("comments", ""),
        "createdBy": created_by,
        "updatedBy": updated_by,
        "createdAt": current_time,
        "updatedAt": current_time
    }
    assignment_serializer = MaintenanceAssignmentSerializer(data=assignment_data)
    if assignment_serializer.is_valid():
        assignment_serializer.save()
        return Response({"data": assignment_serializer.data}, status=status.HTTP_200_OK)
    else:
        return Response({"error": assignment_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import MaintenanceType, MaintenanceStaffRoles, MaintenanceStaff

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import MaintenanceType, MaintenanceStaffRoles, MaintenanceStaff

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .models import MaintenanceStaff

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from hotel_app.models import MaintenanceStaff

@api_view(['DELETE'])
def delete_staff_from_role(request, staffId, roleId):
    try:
        # Step 1: Filter the specific MaintenanceStaff mapping
        assignment = MaintenanceStaff.objects.filter(staffId=staffId, roleId=roleId)

        if not assignment.exists():
            return Response({"error": "Staff-role mapping not found."},
                            status=status.HTTP_404_NOT_FOUND)

        # Step 2: Delete only the matching assignment
        deleted_count = assignment.delete()[0]

        # Step 3: Respond with success
        return Response({"message": f"staff deleted successfully."},
                        status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from .models import StaffManagement
from hotel_app.serializers import MaintenanceStaffSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from hotel_app.models import MaintenanceStaff, MaintenanceStaffRoles


@api_view(['GET'])
def get_staff_not_in_role(request, roleId):
    try:
        # Step 1: Find all staff members
        maintenance_staff = MaintenanceStaff.objects.select_related('staffId', 'roleId')

        # Step 2: Prepare unique staff (avoiding duplicates if staff has multiple roles)
        seen = set()
        output = []

        for staff in maintenance_staff:
            # Step 3: Exclude staff who have the selected role (e.g., Plumber)
            if staff.roleId.roleId == roleId:
                continue

            # Step 4: Check if the staff has the selected role, if so, exclude them from the result
            if staff.staffId.staffId not in seen:
                # Step 5: Exclude staff having the selected role entirely (even if they have other roles)
                # This means, if the staff has the role we are excluding (e.g., Plumber), skip them.
                if not MaintenanceStaff.objects.filter(staffId=staff.staffId, roleId=roleId).exists():
                    seen.add(staff.staffId.staffId)
                    output.append({
                        "staffId": staff.staffId.staffId,
                        "staffName": staff.staffId.name,  # Staff name
                        "roleName": staff.roleId.get_roleName_display(),  # Role name
                    })

        # Step 6: Return the response with the list of staff who don't have the selected role
        return Response(output, status=status.HTTP_200_OK)

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from hotel_app.models import Taxes
from hotel_app.serializers import TaxesSerializer

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from hotel_app.models import Taxes
from hotel_app.serializers import TaxesSerializer


@api_view(['GET', 'POST'])
def taxes_list_create(request):
    if request.method == 'GET':
        # If taxId is provided in the query parameters, fetch the specific tax
        taxId = request.query_params.get('taxId')
        if taxId:
            try:
                tax = Taxes.objects.get(taxId=taxId)
                serializer = TaxesSerializer(tax)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Taxes.DoesNotExist:
                return Response({"error": "Tax not found."}, status=status.HTTP_404_NOT_FOUND)

        # Otherwise, return a list of all taxes
        taxes = Taxes.objects.all()
        serializer = TaxesSerializer(taxes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == 'POST':
        # If the type is "Extra Service", category is required
        type = request.data.get('type')

        # If type is "Rent", ensure that category is null
        if type == "Rent":
            request.data['category'] = None  # Explicitly set category to null

        if type == "Extra Service" and not request.data.get('category'):
            return Response({"error": "Category is required for Extra Service tax type."},
                            status=status.HTTP_400_BAD_REQUEST)
        input_data = request.data
        user = User.objects.filter(userId=2).first()
        createdBy = user.pk
        updatedBy = user.pk
        input_data["createdBy"] = createdBy
        input_data["updatedBy"] = updatedBy
        # Serialize and save the new tax
        serializer = TaxesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from hotel_app.models import Taxes
from hotel_app.serializers import TaxesSerializer


@api_view(['PUT'])
def update_tax(request, taxId):
    try:
        tax = Taxes.objects.get(taxId=taxId)
    except Taxes.DoesNotExist:
        return Response({"error": "Tax not found."}, status=status.HTTP_404_NOT_FOUND)

    # Validate that category is provided if type is "Extra Service"
    type = request.data.get('type')
    if type == "Extra Service" and not request.data.get('category'):
        return Response({"error": "Category is required for Extra Service tax type."},
                        status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(userId=2).first()
    input_data = request.data
    input_data['updatedBy'] = user.pk
    input_data['updatedAt'] = now()
    serializer = TaxesSerializer(tax, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from datetime import datetime
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .models import Booking, Checkout
from .serializers import CheckoutSerializer

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from .models import Booking, Checkout
from .serializers import CheckoutSerializer

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime

from .models import Booking, Checkout, Rooms  # Make sure Room is imported
from .serializers import CheckoutSerializer


@api_view(['POST'])
def create_checkout(request):
    if request.method == 'POST':
        print(f"Received data: {request.data}")
        data = request.data

        try:
            # Required fields check
            required_fields = [
                'bookingId', 'roomNo', 'roomType', 'checkinDate', 'checkoutDate',
                'checkinTime', 'checkoutTime', 'totalRent', 'additionalCharges'
            ]
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return Response(
                    {"error": f"Missing required fields: {', '.join(missing_fields)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user = User.objects.filter(userId=2).first()
            if not user:
                return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
            createdBy = user
            updatedBy = user
            createdAt = datetime.now()
            updatedAt = datetime.now()

            # Fetch booking instance
            booking_instance = Booking.objects.get(bookingId=data['bookingId'])

            # Parse dates
            try:
                checkin_date = datetime.strptime(data['checkinDate'].strip(), '%d-%m-%Y').date()
                checkout_date = datetime.strptime(data['checkoutDate'].strip(), '%d-%m-%Y').date()
            except ValueError as e:
                return Response({"error": f"Invalid date format: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

            # Create Checkout instance
            checkout = Checkout(
                bookingId=booking_instance,
                roomNo=data['roomNo'],
                roomType=data['roomType'],
                checkinDate=checkin_date,
                checkinTime=data['checkinTime'],
                extraserviceTotalAmount=data.get('extraserviceTotalAmount', 0.0),
                checkoutDate=checkout_date,
                checkoutTime=data['checkoutTime'],
                totalRent=data['totalRent'],
                additionalCharges=data['additionalCharges'],
                remarks=data.get('remarks', ''),
                stateGST=data.get('stateGST', 0.00),
                centralGST=data.get('centralGST', 0.00),
                discount=data.get('discount', 0.0),
                checkinAdvance=data.get('checkinAdvance', 0.0),
                createdBy = createdBy,
                updatedBy = updatedBy,
                createdAt = createdAt,
                updatedAt = updatedAt,
            )
            checkout.save()

            # Mark room as unoccupied
            room_id = booking_instance.roomId
            try:
                room = Rooms.objects.get(id=room_id)
                room.status = 'unoccupied'
                room.save()
            except Rooms.DoesNotExist:
                return Response({"error": "Associated room not found"}, status=status.HTTP_404_NOT_FOUND)

            # Serialize and return
            serializer = CheckoutSerializer(checkout)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Booking.DoesNotExist:
            return Response({"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)
        except KeyError as e:
            return Response({"error": f"Missing key: {e}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import ExtraServiceCategory
from .serializers import ExtraServiceCategorySerializer


@api_view(['GET'])
def get_all_extra_service_categories(request):
    categories = ExtraServiceCategory.objects.all()
    serializer = ExtraServiceCategorySerializer(categories, many=True)
    return Response(serializer.data)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import ExtraService


@api_view(['GET'])
def get_category_name(request, service_id):
    try:
        # Fetch the extra service with the given serviceId
        service = ExtraService.objects.get(serviceId=service_id)

        # Get the category related to the service
        category = service.categoryId  # This is the ForeignKey field

        if category:
            # Return the category name
            return Response({'categoryName': category.categoryName}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Category not found for the service'}, status=status.HTTP_404_NOT_FOUND)

    except ExtraService.DoesNotExist:
        return Response({'error': 'Service not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import ExtraService
from .serializers import ExtraServiceSerializer


@api_view(['GET'])
def get_unpaid_services(request):
    unpaid_services = ExtraService.objects.filter(paymentStatus='Unpaid')
    serializer = ExtraServiceSerializer(unpaid_services, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def create_payment_checkout(request):
    # Log the data received from the frontend
    print(f"Received data from frontend: {request.data}")

    data = request.data.copy()

    # Check if bookingId and totalAmount are provided
    if data.get('bookingId') and data.get('totalAmount'):
        data['paymentRemarks'] = 'Checkout'

    user = User.objects.filter(userId=2).first()
    if not user:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    # Adding createdBy, updatedBy, createdAt, and updatedAt to the input data
    createdBy = user.pk
    updatedBy = user.pk
    createdAt = updatedAt = datetime.now()

    # Add these fields to the data dictionary
    data["createdBy"] = createdBy
    data["updatedBy"] = updatedBy
    data["createdAt"] = createdAt
    data["updatedAt"] = updatedAt

    serializer = PaymentCheckoutSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import ExtraService
from django.db.models import Sum


@api_view(['GET'])
def get_total_extra_services(request, bookingId):
    # Retrieve all extra services for the provided bookingId
    extra_services = ExtraService.objects.filter(bookingId=bookingId)

    # Sum the serviceCost of all extra services
    total_cost = extra_services.aggregate(Sum('serviceCost'))['serviceCost__sum'] or 0

    return Response({'bookingId': bookingId, 'extraservicetotalAmount': total_cost}, status=status.HTTP_200_OK)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Rooms


@api_view(['PUT'])
def update_room_status(request, room_no):
    try:
        room = Rooms.objects.get(roomNumber=room_no)  # Find room by its room number
        room.status = request.data.get('status', room.status)  # Update status or keep the current one
        room.save()

        return Response({"message": "Room status updated successfully."}, status=status.HTTP_200_OK)

    except Rooms.DoesNotExist:
        return Response({"error": "Room not found."}, status=status.HTTP_404_NOT_FOUND)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Checkout
from .serializers import CheckoutSerializer


@api_view(['GET'])
def get_all_checkouts(request):
    try:
        checkouts = Checkout.objects.all().order_by('-checkoutDate')
        serializer = CheckoutSerializer(checkouts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



import os
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.files.storage import default_storage
from .models import Customer, ImageProof

@api_view(['POST'])
def upload_image_proof(request):
    customer_id = request.data.get('customerId')
    if not customer_id:
        return Response({"error": "customerId is required."}, status=400)

    try:
        customer = Customer.objects.get(customerId=customer_id)
    except Customer.DoesNotExist:
        return Response({"error": "Customer not found."}, status=404)

    proof_name = request.data.get('name', 'ID Proof')

    photos_files = request.FILES.getlist('photos')
    if not photos_files:
        return Response({"error": "Please upload at least one photo."}, status=400)

    # Save photos
    photo_paths = []
    for photo in photos_files:
        path = default_storage.save(os.path.join('uploads', photo.name), photo)
        photo_paths.append(path)

    # Create ImageProof record
    image_proof = ImageProof.objects.create(
        customer=customer,
        name=proof_name,
        photos=photo_paths
    )

    # Custom response (without id)
    response_data = {
        "customerId": customer.customerId,
        "name": image_proof.name,
        "photos": image_proof.photos
    }

    return Response(response_data, status=201)


@api_view(['GET'])
def get_all_customer(request):
    customers=Customer.objects.all()
    serializer=CustomerListSerializer(customers,many=True)
    return Response(serializer.data)
