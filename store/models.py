import io
import os
from decimal import Decimal
from PIL import Image, ImageDraw, ImageFont
from django.core.files.storage import default_storage
from django.core.files import File
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.utils import timezone
from django.db import models
from django.conf import settings
BASE_DIR = settings.BASE_DIR
from django.contrib.auth.models import AbstractUser
from cloudinary.models import CloudinaryField
from cloudinary.uploader import upload



class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('gamer', 'Gamer'),
        ('developer', 'Developer'),
        ('admin', 'Admin'),
    ]
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=25, unique=True)   
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, null=True, blank=True)
    bio = models.TextField(blank=True)
    email = models.EmailField()
    profile_picture = CloudinaryField('profile_picture', blank=True, null=True)
    account_created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.is_superuser and self.user_type != 'admin':
            self.user_type = 'admin'
        super().save(*args, **kwargs)
    
    def set_default_profile_picture(self):
        """Set the default profile picture for the user"""
        default_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'default-profile-photo.png')
        
        if not self.profile_picture and os.path.exists(default_path):
            try:
                # Upload to cloudinary
                upload_result = upload(
                    default_path,
                    folder="profile_pictures",
                    public_id=f"default_{self.username}",
                    overwrite=True
                )
                # Set the CloudinaryField
                self.profile_picture = upload_result['public_id']
                self.save()
            except Exception as e:
                print(f"Error setting default profile picture: {e}")
    
    def __str__(self):
        return f"User: {self.username}"


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
    price = models.DecimalField(
        max_digits=6, 
        decimal_places=2,
        validators=[
            MinValueValidator(
                Decimal('0.50'), 
                message="Price must be at least €0.50"
            )
        ]
    )    
    developer = models.ForeignKey(User, on_delete=models.CASCADE)
    is_published = models.BooleanField(default=False)
    thumbnail = CloudinaryField('thumbnail', blank=True, null=True, help_text="Recommended image ratio: 7:5")
    created_at = models.DateTimeField(default=timezone.now)  

    def __str__(self):
        return f"Game: {self.title}"
    
    class Meta:
        ordering = ['-created_at']
    
    def get_thumbnail(self):
        if self.thumbnail:
            return self.thumbnail.url
        else:
            return self.generate_default_thumbnail()

    def get_developer_name(self):
        return self.developer.username

    def generate_default_thumbnail(self):
        # Create a square bright yellow image
        img_size = (400, 400)
        img = Image.new('RGB', img_size, color='#FFC246')  # Bright yellow color
        d = ImageDraw.Draw(img)
        
        # Use Oxanium font with a larger size
        font_size = 40
        font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'Oxanium-Bold.ttf')
        try:
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            font = ImageFont.load_default().font_variant(size=font_size)
        
        # Draw the text
        text = self.title
        left, top, right, bottom = d.textbbox((0, 0), text, font=font)
        text_width = right - left
        text_height = bottom - top
        x = (img_size[0] - text_width) / 2
        y = (img_size[1] - text_height) / 2
        d.text((x, y), text, font=font, fill='#993333')  # Dark accent color
        
        # Save the image to a bytes buffer
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Upload the image to Cloudinary
        result = upload(buffer, folder="game_thumbnails", public_id=f"{self.title}_default")
        
        # Save the Cloudinary URL to the thumbnail field
        self.thumbnail = result['url']
        self.save()
        
        return self.thumbnail

    def get_average_rating(self):
        reviews = self.review_set.all()
        if not reviews:
            return 0
        total_rating = sum(review.rating for review in reviews)
        return total_rating / len(reviews)
    
    def get_review_count(self):
        return self.review_set.count()

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
        return f"Order by {self.customer} as part of Order {self.order_id}"

class OrderLine(models.Model):
    orderline_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Orderline: {self.game} as part of Order {self.order_id}"

class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    like_count = models.IntegerField(default=0)

    def update_like_count(self):
        """Updates the like_count based on ReviewVotes"""
        upvotes = self.votes.filter(vote_type='up').count()
        downvotes = self.votes.filter(vote_type='down').count()
        self.like_count = upvotes - downvotes
        self.save()
    def __str__(self):
        return f"Review by {self.customer} for {self.game}"

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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField(max_length=3000)
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message: {self.message_id} from {self.user}"

class InboxMessage(models.Model):
    message_id = models.AutoField(primary_key=True)
    developer = models.ForeignKey(User, on_delete=models.CASCADE)
    game_title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=[('approved', 'Approved'), ('rejected', 'Rejected')])

    def __str__(self):
        return f"Message for {self.developer} about {self.game_title}"

class ReviewVote(models.Model):
    VOTE_CHOICES = [
        ('up', 'Upvote'),
        ('down', 'Downvote')
    ]
    
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vote_type = models.CharField(max_length=4, choices=VOTE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('review', 'user')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.review.update_like_count()
    def delete(self, *args, **kwargs):
        review = self.review
        super().delete(*args, **kwargs)
        review.update_like_count()
    def __str__(self):
        return f"{self.user}'s {self.vote_type} vote on {self.review}"