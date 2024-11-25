from django.db import models

class StockData(models.Model):
    symbol = models.CharField(max_length=10)
    timestamp = models.DateTimeField()
    open_price = models.FloatField()
    high_price = models.FloatField()
    low_price = models.FloatField()
    close_price = models.FloatField()
    volume = models.IntegerField()

    class Meta:
        verbose_name = "Stock Data"
        verbose_name_plural = "Stock Data"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.symbol} - {self.timestamp}"