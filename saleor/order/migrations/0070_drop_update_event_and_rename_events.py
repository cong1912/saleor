# Generated by Django 2.2 on 2019-05-07 10:13

from enum import Enum

from django.db import migrations
from django.db.models import CharField

from saleor.order.events import OrderEvents


class OldOrderEvents(Enum):
    PLACED = "placed"
    PLACED_FROM_DRAFT = "draft_placed"
    OVERSOLD_ITEMS = "oversold_items"
    ORDER_MARKED_AS_PAID = "marked_as_paid"
    CANCELED = "canceled"
    ORDER_FULLY_PAID = "order_paid"
    UPDATED = "updated"

    EMAIL_SENT = "email_sent"

    PAYMENT_CAPTURED = "captured"
    PAYMENT_REFUNDED = "refunded"
    PAYMENT_VOIDED = "voided"

    FULFILLMENT_CANCELED = "fulfillment_canceled"
    FULFILLMENT_RESTOCKED_ITEMS = "restocked_items"
    FULFILLMENT_FULFILLED_ITEMS = "fulfilled_items"
    TRACKING_UPDATED = "tracking_updated"
    NOTE_ADDED = "note_added"

    OTHER = "other"


def _replace_old_namings(apps, *_args, **_kwargs):
    cls = apps.get_model("order", "OrderEvent")

    for event_type in OldOrderEvents:
        cls.objects.filter(type=event_type.value).update(type=event_type.name.lower())


def _move_updated_events_to_other(apps, *_args, **_kwargs):
    cls = apps.get_model("order", "OrderEvent")

    for event in cls.objects.filter(type="updated").all():
        event.type = OrderEvents.OTHER
        event.parameters["message"] = "Order details were updated by %(user_name)s" % {
            "user_name": event.user
        }
        event.save(update_fields=["type", "parameters"])


class Migration(migrations.Migration):

    dependencies = [("order", "0069_auto_20190225_2305")]

    operations = [
        migrations.RunPython(_move_updated_events_to_other),
        migrations.RunPython(_replace_old_namings),
        migrations.AlterField(
            model_name="orderevent",
            name="type",
            field=CharField(
                choices=[
                    ("DRAFT_CREATED", "draft_created"),
                    ("DRAFT_ADDED_PRODUCTS", "draft_added_products"),
                    ("DRAFT_REMOVED_PRODUCTS", "draft_removed_products"),
                    ("PLACED", "placed"),
                    ("PLACED_FROM_DRAFT", "placed_from_draft"),
                    ("OVERSOLD_ITEMS", "oversold_items"),
                    ("CANCELED", "canceled"),
                    ("ORDER_MARKED_AS_PAID", "order_marked_as_paid"),
                    ("ORDER_FULLY_PAID", "order_fully_paid"),
                    ("UPDATED_ADDRESS", "updated_address"),
                    ("EMAIL_SENT", "email_sent"),
                    ("PAYMENT_CAPTURED", "payment_captured"),
                    ("PAYMENT_REFUNDED", "payment_refunded"),
                    ("PAYMENT_VOIDED", "payment_voided"),
                    ("PAYMENT_FAILED", "payment_failed"),
                    ("FULFILLMENT_CANCELED", "fulfillment_canceled"),
                    ("FULFILLMENT_RESTOCKED_ITEMS", "fulfillment_restocked_items"),
                    ("FULFILLMENT_FULFILLED_ITEMS", "fulfillment_fulfilled_items"),
                    ("TRACKING_UPDATED", "tracking_updated"),
                    ("NOTE_ADDED", "note_added"),
                    ("OTHER", "other"),
                ],
                max_length=255,
            ),
        ),
    ]
