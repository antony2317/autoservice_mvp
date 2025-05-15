# from datetime import datetime, time, timedelta
# from .models import Booking
#
# def get_available_time_slots(service_center, date_str):
#     date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
#     start_hour = 9
#     end_hour = 18
#     slot_duration = timedelta(minutes=60)
#
#     existing_bookings = Booking.objects.filter(
#         service__autoservice=service_center,
#         date=date_obj
#     ).values_list('time', flat=True)
#
#     slots = []
#     current_time = time(start_hour, 0)
#     while current_time < time(end_hour, 0):
#         if current_time not in existing_bookings:
#             slots.append(current_time.strftime('%H:%M'))
#         current_time = (datetime.combine(date_obj, current_time) + slot_duration).time()
#     return slots
