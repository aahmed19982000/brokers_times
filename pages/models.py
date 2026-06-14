from django.db import models

class HomepageSettings(models.Model):
    # Hero popular review
    hero_featured_broker = models.ForeignKey('brokers.Broker', on_delete=models.SET_NULL, null=True, blank=True, related_name='hero_featured')
    
    # Top Rated Trading Brokers (3 positions)
    featured_broker_1 = models.ForeignKey('brokers.Broker', on_delete=models.SET_NULL, null=True, blank=True, related_name='featured_pos_1')
    featured_broker_2 = models.ForeignKey('brokers.Broker', on_delete=models.SET_NULL, null=True, blank=True, related_name='featured_pos_2')
    featured_broker_3 = models.ForeignKey('brokers.Broker', on_delete=models.SET_NULL, null=True, blank=True, related_name='featured_pos_3')
    
    # Curated Lists (4 positions)
    featured_list_1 = models.ForeignKey('best_brokers.BestBrokersList', on_delete=models.SET_NULL, null=True, blank=True, related_name='featured_list_pos_1')
    featured_list_2 = models.ForeignKey('best_brokers.BestBrokersList', on_delete=models.SET_NULL, null=True, blank=True, related_name='featured_list_pos_2')
    featured_list_3 = models.ForeignKey('best_brokers.BestBrokersList', on_delete=models.SET_NULL, null=True, blank=True, related_name='featured_list_pos_3')
    featured_list_4 = models.ForeignKey('best_brokers.BestBrokersList', on_delete=models.SET_NULL, null=True, blank=True, related_name='featured_list_pos_4')

    class Meta:
        verbose_name = "Homepage Settings"
        verbose_name_plural = "Homepage Settings"
        
    def __str__(self):
        return "Homepage Configuration"
