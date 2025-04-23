from django.db import models
from django.utils import timezone

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=100)
    diameter = models.FloatField(help_text='Diameter in inches')
    length = models.FloatField(help_text='Length in feet')
    quantity = models.IntegerField(default=0)
    import_date = models.DateField(default=timezone.now)
    image = models.ImageField(upload_to='warehouse_images/', null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.diameter}\" x {self.length}'"

class WaterPipeCountHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='count_history')
    count = models.IntegerField()
    timestamp = models.DateTimeField(default=timezone.now)
    original_image = models.ImageField(upload_to='history/original/', null=True, blank=True)
    processed_image = models.ImageField(upload_to='history/processed/', null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Water Pipe Count History"
        verbose_name_plural = "Water Pipe Count History Records"

    def __str__(self):
        return f"{self.product.name} - {self.count} pipes at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
