# Generated by Django 5.2 on 2025-04-07 08:37

import pgvector.django.vector
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0004_alter_review_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='embedding',
            field=pgvector.django.vector.VectorField(blank=True, default=None, dimensions=384, null=True),
        ),
    ]
