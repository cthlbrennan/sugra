from django.db import models
from django.contrib.auth.models import AbstractUser
from cloudinary.models import CloudinaryField

class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('regular', 'Regular'),
        ('admin', 'Admin'),
    ]
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=25, unique=True)   
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    bio = models.TextField(blank=True)
    email = models.EmailField()  #unique = true ?
    profile_picture = CloudinaryField('profile_picture', blank=True, null=True)
    account_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
    return f"User: {self.user}"

class Game(models.Model):
    GAME_GENRE_CHOICES = [
    ('action_adventure', 'Action Adventure Game'),
    ('action_rpg', 'Action RPG'),
    ('adventure', 'Adventure'),
    ('casual', 'Casual'),
    ('fighting', 'Fighting'),
    ('first_person_shooter', 'First Person Shooter'),
    ('mmo', 'Massively Multiplayer Online'),
    ('platform', 'Platformer'),
    ('puzzle', 'Puzzle'),
    ('party', 'Party'),
    ('racing', 'Racing'),
    ('rpg', 'RPG'),
    ('sandbox', 'Sandbox'),
    ('shooter', 'Shooter'),
    ('simulation', 'Simulation'),
    ('stealth', 'Stealth'),
    ('strategy', 'Strategy'),
    ('survival_horror', 'Survival Horror'),
    ('sports', 'Sports'),
    ]
    game_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField(max_length=3000)
    genre = models.CharField(max_length=100, choices=GAME_GENRE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    developer = models.ForeignKey(User, on_delete=models.CASCADE)
    release_date = models.DateField()
    is_published = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    thumbnail = CloudinaryField('thumbnail', blank=True, null=True)

    def __str__(self):
    return f"Game: {self.title}"

class Wishlist(models.Model):
    wishlist_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    games = models.ManyToManyField(Game)

    def __str__(self):
    return f"Wishlist for {self.user}"

class Order(models.Model):
    order_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_pid = models.CharField(max_length=255)

    def __str__(self):
    return f"Order by {self.customer} as part of Order {self.order}"

class OrderLine(models.Model):
    orderline_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
    return f"Orderline: {self.game} as part of Order {self.order}"

class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    like_count = models.IntegerField(default=0)

    def __str__(self):
    return f"Review by {self.customer} for {self.game}"

class Screenshot(models.Model):
    screenshot_id = models.AutoField(primary_key=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    image = CloudinaryField('screenshot')
    alt_text = models.CharField(max_length=255)

    def __str__(self):
    return f"Screenshot {self.screenshot_id} for {self.game}"

class Message(models.Model):
    message_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=3000)
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
    return f"Message: {self.message_id} from {self.user}"