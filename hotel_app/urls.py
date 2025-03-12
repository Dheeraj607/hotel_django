from django.urls import path, include
from .views import rooms_available, rooms, book_room_and_payment, payment_detail, all_room_details,create_payment_with_extras
from .views import get_all_extra_services,payment_for_service,refund_operations
urlpatterns = [
    path('rooms/', rooms, name='rooms'),
    path('book-room/', book_room_and_payment, name='book-room'),
    path('payment/<int:booking_id>/', payment_detail, name='payment-detail'),
    path('room_details/', all_room_details, name='room-details'),
    path('payment_with_extras/', create_payment_with_extras, name='payment-with-extras'),
    path('extra_services/', get_all_extra_services, name='get_all_extra_services'),
    path('payment_service/', payment_for_service, name='payment_for_service'),
    path('refund/', refund_operations, name='refund_operations_create'),




]

