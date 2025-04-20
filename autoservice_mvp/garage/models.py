import datetime

from django.contrib.auth import get_user_model
from django.db import models
from account.models import User


class Garage(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название автосервиса")
    address = models.TextField(blank=True, verbose_name="Адрес")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    specialization = models.CharField(max_length=100, blank=True, verbose_name="Специализация")

    class Meta:
        verbose_name = "Автосервис"
        verbose_name_plural = "Автосервисы"
        ordering = ['name']

    def __str__(self):
        return self.name


CAR_BRANDS = [
    ('Toyota', 'Toyota'),
    ('Honda', 'Honda'),
    ('BMW', 'BMW'),
    ('Mercedes-Benz', 'Mercedes-Benz'),
    ('Audi', 'Audi'),
    ('Volkswagen', 'Volkswagen'),
    ('Ford', 'Ford'),
    ('Chevrolet', 'Chevrolet'),
    ('Nissan', 'Nissan'),
    ('Hyundai', 'Hyundai'),
    ('Kia', 'Kia'),
    ('Subaru', 'Subaru'),
    ('Mazda', 'Mazda'),
    ('Lexus', 'Lexus'),
    ('Volvo', 'Volvo'),
    ('Jeep', 'Jeep'),
    ('Tesla', 'Tesla'),
    ('Porsche', 'Porsche'),
    ('Land Rover', 'Land Rover'),
    ('Jaguar', 'Jaguar'),
    ('Mitsubishi', 'Mitsubishi'),
    ('Fiat', 'Fiat'),
    ('Peugeot', 'Peugeot'),
    ('Renault', 'Renault'),
    ('Citroën', 'Citroën'),
    ('Skoda', 'Skoda'),
    ('Seat', 'Seat'),
    ('Opel', 'Opel'),
    ('Suzuki', 'Suzuki'),
    ('Dacia', 'Dacia'),
    ('Alfa Romeo', 'Alfa Romeo'),
    ('Chrysler', 'Chrysler'),
    ('Dodge', 'Dodge'),
    ('Infiniti', 'Infiniti'),
    ('Acura', 'Acura'),
    ('Buick', 'Buick'),
    ('Cadillac', 'Cadillac'),
    ('GMC', 'GMC'),
    ('Lincoln', 'Lincoln'),
    ('Mini', 'Mini'),
    ('Smart', 'Smart'),
    ('Ferrari', 'Ferrari'),
    ('Lamborghini', 'Lamborghini'),
    ('Maserati', 'Maserati'),
    ('Bentley', 'Bentley'),
    ('Rolls-Royce', 'Rolls-Royce'),
    ('Aston Martin', 'Aston Martin'),
    ('McLaren', 'McLaren'),
    ('Bugatti', 'Bugatti'),
    ('Lada', 'Lada'),
    ('Geely', 'Geely'),
    ('BYD', 'BYD'),
    ('Great Wall', 'Great Wall'),
    ('Chery', 'Chery'),
    ('Haval', 'Haval'),
    ('Genesis', 'Genesis'),
    ('Rivian', 'Rivian'),
    ('Lucid', 'Lucid'),
]

CAR_MODELS = {
    'Toyota': ['Camry', 'Corolla', 'RAV4', 'Prius', 'Highlander', 'Tacoma', 'Hilux', 'Land Cruiser', 'Supra'],
    'Honda': ['Accord', 'Civic', 'CR-V', 'Pilot', 'HR-V', 'Odyssey', 'Fit', 'Ridgeline'],
    'BMW': ['3 Series', '5 Series', '7 Series', 'X3', 'X5', 'X7', 'M3', 'M5', 'i4', 'iX'],
    'Mercedes-Benz': ['C-Class', 'E-Class', 'S-Class', 'GLC', 'GLE', 'GLA', 'A-Class', 'AMG GT'],
    'Audi': ['A4', 'A6', 'A8', 'Q3', 'Q5', 'Q7', 'e-tron', 'RS6', 'TT'],
    'Volkswagen': ['Golf', 'Passat', 'Tiguan', 'Polo', 'Jetta', 'Arteon', 'ID.4', 'Touareg'],
    'Ford': ['F-150', 'Focus', 'Mustang', 'Explorer', 'Escape', 'Ranger', 'Bronco', 'Transit'],
    'Chevrolet': ['Camaro', 'Corvette', 'Malibu', 'Silverado', 'Equinox', 'Tahoe', 'Traverse', 'Spark'],
    'Nissan': ['Altima', 'Sentra', 'Rogue', 'Pathfinder', 'Qashqai', 'X-Trail', 'Murano', 'GT-R'],
    'Hyundai': ['Elantra', 'Sonata', 'Tucson', 'Santa Fe', 'Kona', 'Palisade', 'i20', 'i30'],
    'Kia': ['Rio', 'Optima', 'Sportage', 'Sorento', 'Stinger', 'Telluride', 'Ceed', 'EV6'],
    'Subaru': ['Impreza', 'Outback', 'Forester', 'Legacy', 'Crosstrek', 'BRZ', 'WRX'],
    'Mazda': ['Mazda3', 'Mazda6', 'CX-5', 'CX-30', 'CX-9', 'MX-5 Miata', 'RX-8'],
    'Lexus': ['ES', 'RX', 'NX', 'LS', 'GX', 'LX', 'IS', 'LC'],
    'Volvo': ['S60', 'S90', 'XC40', 'XC60', 'XC90', 'V60', 'V90'],
    'Jeep': ['Wrangler', 'Grand Cherokee', 'Cherokee', 'Renegade', 'Compass', 'Gladiator'],
    'Tesla': ['Model 3', 'Model S', 'Model X', 'Model Y', 'Cybertruck', 'Roadster'],
    'Porsche': ['911', 'Cayenne', 'Panamera', 'Macan', 'Taycan', 'Boxster', 'Cayman'],
    'Land Rover': ['Range Rover', 'Range Rover Sport', 'Discovery', 'Defender', 'Evoque'],
    'Jaguar': ['XF', 'XJ', 'F-Pace', 'E-Pace', 'I-Pace', 'XE'],
    'Mitsubishi': ['Outlander', 'Pajero', 'Lancer', 'ASX', 'Eclipse Cross', 'Mirage'],
    'Fiat': ['500', 'Panda', 'Tipo', 'Doblo', '500X', '500L'],
    'Peugeot': ['208', '308', '508', '2008', '3008', '5008'],
    'Renault': ['Clio', 'Megane', 'Captur', 'Kadjar', 'Duster', 'Arkana', 'Zoe'],
    'Citroën': ['C3', 'C4', 'C5', 'Berlingo', 'C3 Aircross', 'C5 Aircross'],
    'Skoda': ['Octavia', 'Superb', 'Kodiaq', 'Karoq', 'Fabia', 'Scala', 'Enyaq'],
    'Seat': ['Leon', 'Ibiza', 'Ateca', 'Arona', 'Tarraco', 'Cupra Formentor'],
    'Opel': ['Corsa', 'Astra', 'Insignia', 'Mokka', 'Crossland', 'Grandland'],
    'Suzuki': ['Swift', 'Vitara', 'S-Cross', 'Jimny', 'Ignis', 'Baleno'],
    'Dacia': ['Sandero', 'Logan', 'Duster', 'Spring', 'Jogger', 'Lodgy'],
    'Alfa Romeo': ['Giulia', 'Stelvio', 'Tonale', '4C', 'Brera', '159'],
    'Chrysler': ['300', 'Pacifica', 'Voyager', 'Grand Caravan'],
    'Dodge': ['Challenger', 'Charger', 'Durango', 'Journey'],
    'Infiniti': ['Q50', 'Q60', 'QX50', 'QX60', 'QX80'],
    'Acura': ['TLX', 'MDX', 'RDX', 'NSX', 'Integra'],
    'Buick': ['Encore', 'Enclave', 'Regal', 'LaCrosse'],
    'Cadillac': ['CT5', 'Escalade', 'XT4', 'XT5', 'XT6'],
    'GMC': ['Sierra', 'Yukon', 'Acadia', 'Canyon', 'Hummer EV'],
    'Lincoln': ['Navigator', 'Aviator', 'Corsair', 'Nautilus'],
    'Mini': ['Cooper', 'Countryman', 'Clubman', 'Paceman'],
    'Smart': ['Fortwo', 'Forfour', 'EQ Fortwo'],
    'Ferrari': ['488', 'F8 Tributo', 'Roma', 'SF90', 'LaFerrari'],
    'Lamborghini': ['Huracan', 'Aventador', 'Urus', 'Revuelto'],
    'Maserati': ['Ghibli', 'Quattroporte', 'Levante', 'MC20'],
    'Bentley': ['Continental GT', 'Bentayga', 'Flying Spur', 'Mulsanne'],
    'Rolls-Royce': ['Phantom', 'Ghost', 'Cullinan', 'Wraith', 'Dawn'],
    'Aston Martin': ['DB11', 'Vantage', 'DBS', 'Valhalla'],
    'McLaren': ['720S', 'Artura', 'GT', 'P1', 'Senna'],
    'Bugatti': ['Chiron', 'Veyron', 'Divo', 'Bolide'],
    'Lada': ['Granta', 'Vesta', 'Niva', 'XRAY', 'Largus'],
    'Geely': ['Coolray', 'Atlas', 'Emgrand', 'Tugella', 'Monjaro'],
    'BYD': ['Han', 'Tang', 'Song', 'Yuan', 'Seal', 'Dolphin'],
    'Great Wall': ['Haval H6', 'Tank 300', 'Poer', 'Wey Coffee 01'],
    'Chery': ['Tiggo 7', 'Tiggo 8', 'Arrizo 6', 'OMODA 5'],
    'Haval': ['H6', 'Jolion', 'F7', 'Dargo', 'H9'],
    'Genesis': ['G70', 'G80', 'G90', 'GV70', 'GV80'],
    'Rivian': ['R1T', 'R1S', 'EDV'],
    'Lucid': ['Air', 'Gravity'],
}


def get_year_choices():
    current_year = datetime.datetime.now().year
    return [(year, year) for year in range(current_year, current_year - 30, -1)]


class Car(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cars')

    # Поле с выбором марки
    brand = models.CharField(
        max_length=50,
        choices=CAR_BRANDS,
        verbose_name='Марка автомобиля'
    )

    # Поле с выбором модели (будет заполняться динамически через JS)
    model = models.CharField(
        max_length=50,
        verbose_name='Модель автомобиля'
    )

    # Поле с выбором года выпуска
    year = models.PositiveIntegerField(
        choices=get_year_choices(),
        verbose_name='Год выпуска'
    )

    vin = models.CharField(
        max_length=17,
        unique=True,
        blank=True,
        null=True,
        verbose_name='VIN-номер'
    )

    mileage = models.PositiveIntegerField(
        default=0,
        verbose_name='Пробег (км)'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления'
    )

    def __str__(self):
        return f"{self.get_brand_display()} {self.model} ({self.year})"

    class Meta:
        verbose_name = 'Автомобиль'
        verbose_name_plural = 'Автомобили'


class ServiceRecord(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    garage = models.ForeignKey(Garage, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField()  # Дата обслуживания
    mileage = models.PositiveIntegerField()  # Пробег на момент обслуживания
    service_type = models.CharField(max_length=100, verbose_name='Вид работ')  # Вид работ ("Замена масла")
    description = models.TextField(blank=True)  # Детали
    cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='Цена')  # Стоимость
    receipt = models.FileField(upload_to='service_receipts/', blank=True, verbose_name='фото чека(не обязательно)')  # Чек (PDF/фото)
    created_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        editable=False,
        verbose_name='Создатель записи'
    )

    def __str__(self):
        return f"{self.service_type} ({self.date})"


class ServiceRequest(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    description = models.TextField()
    desired_date = models.DateTimeField()
    STATUS_CHOICES = [
        ('pending', 'Ожидает предложений'),
        ('accepted', 'Принята'),
        ('completed', 'Завершена'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
