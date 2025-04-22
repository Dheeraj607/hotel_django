from django.urls import path, include

from . import views
from .views import rooms_available, rooms, book_room_and_payment, payment_detail, all_room_details, \
    create_payment_with_extras, MaintenanceTypeListView, add_roles, get_role_details, get_staff_by_type, \
    modify_assignment, get_staff_not_in_role, create_checkout, get_all_extra_service_categories, get_category_name
from .views import get_all_extra_services,payment_for_service,refund_operations,room_inspection,update_booking,maintenance_role_detail,maintenance_roles_list,maintenance_staff_detail,maintenance_staff_list
from .views import create_maintenance_request,get_maintenance_requests_with_staff,update_maintenance_request




urlpatterns = [
    path('rooms/', rooms, name='rooms'),
    path('book-room/', book_room_and_payment, name='book-room'),
    path("book-room/<int:booking_id>/", update_booking, name="update-booking"),
    path('payment/<int:booking_id>/', payment_detail, name='payment-detail'),
    path('room_details/', all_room_details, name='room-details'),
    path('payment_with_extras/', create_payment_with_extras, name='payment-with-extras'),
    path('extra_services/', get_all_extra_services, name='get_all_extra_services'),
    path('payment_service/', payment_for_service, name='payment_for_service'),
    path('refund/', refund_operations, name='refund_operations_create'),
    path('inspections/', room_inspection, name='room_inspection'),
    path('inspections/<int:inspection_id>/', room_inspection, name='room_inspection'),
    path('maintenance-types/', MaintenanceTypeListView.as_view(), name='maintenance-type-list'),
    path('maintenance-roles/', maintenance_roles_list, name='maintenance_roles_list'),  # GET all & POST
    path('maintenance-roles/<int:role_id>/', maintenance_role_detail, name='maintenance_role_detail'),# GET one & PUT
    path('maintenance-staff/', maintenance_staff_list, name='maintenance_staff_list'),  # POST & GET (all)
    path('maintenance-staff/<int:id>/', maintenance_staff_detail, name='maintenance_staff_detail'),# GET (one) & PUT
    path('maintenance-request-with-assignment/', create_maintenance_request, name='create-maintenance-request-assignment'),
    path('maintenance-requests-with-staff/', get_maintenance_requests_with_staff, name='get_maintenance_requests_with_staff'),
    path('maintenance-requests/<str:requestId>/', update_maintenance_request, name='update-maintenance-request'),
    path('add-roles/', add_roles, name='add_multi_role'),
    path('get-roles/<int:id>', get_role_details, name='get_role_details'),
    path('get-staffs/<int:id>', get_staff_by_type, name='get_staff_details'),
    path('modify-assignment/', modify_assignment, name='modify_assignment'),
    path('delete-staff-by-type/<int:staffId>/', views.delete_staff_by_type, name='delete_staff_by_type'),
    path('get_staff_not_in_role/<int:roleId>/', get_staff_not_in_role, name='get_staff_not_in_role'),
    path('taxes/', views.taxes_list_create, name='taxes_list_create'),  # GET all Taxes / POST create a new Tax
    path('taxes/update/<int:taxId>/', views.update_tax, name='update_tax'),
    path('checkout/create/', create_checkout, name='create-checkout'),
    path('extra-service-categories/', get_all_extra_service_categories, name='get_extra_service_categories'),
    path('get-category-name/<int:service_id>/', get_category_name, name='get_category_name'),
]


