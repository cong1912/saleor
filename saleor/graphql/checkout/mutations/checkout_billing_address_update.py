import graphene

from ....checkout import AddressType
from ....checkout.error_codes import CheckoutErrorCode
from ....checkout.utils import change_billing_address_in_checkout
from ....core.tracing import traced_atomic_transaction
from ...account.types import AddressInput
from ...core.descriptions import (
    ADDED_IN_34,
    ADDED_IN_35,
    DEPRECATED_IN_3X_INPUT,
    PREVIEW_FEATURE,
)
from ...core.scalars import UUID
from ...core.types import CheckoutError
from ..types import Checkout
from .checkout_create import CheckoutAddressValidationRules
from .checkout_shipping_address_update import CheckoutShippingAddressUpdate
from .utils import get_checkout


class CheckoutBillingAddressUpdate(CheckoutShippingAddressUpdate):
    checkout = graphene.Field(Checkout, description="An updated checkout.")

    class Arguments:
        id = graphene.ID(
            description="The checkout's ID." + ADDED_IN_34,
            required=False,
        )
        token = UUID(
            description=f"Checkout token.{DEPRECATED_IN_3X_INPUT} Use `id` instead.",
            required=False,
        )
        checkout_id = graphene.ID(
            required=False,
            description=(
                f"The ID of the checkout. {DEPRECATED_IN_3X_INPUT} Use `id` instead."
            ),
        )
        billing_address = AddressInput(
            required=True, description="The billing address of the checkout."
        )
        validation_rules = CheckoutAddressValidationRules(
            required=False,
            description=(
                "The rules for changing validation for received billing address data."
                + ADDED_IN_35
                + PREVIEW_FEATURE
            ),
        )

    class Meta:
        description = "Update billing address in the existing checkout."
        error_type_class = CheckoutError
        error_type_field = "checkout_errors"

    @classmethod
    def perform_mutation(
        cls,
        _root,
        info,
        billing_address,
        validation_rules=None,
        checkout_id=None,
        token=None,
        id=None,
    ):
        checkout = get_checkout(
            cls,
            info,
            checkout_id=checkout_id,
            token=token,
            id=id,
            error_class=CheckoutErrorCode,
        )

        address_validation_rules = validation_rules or {}
        billing_address = cls.validate_address(
            billing_address,
            address_type=AddressType.BILLING,
            instance=checkout.billing_address,
            info=info,
            format_check=address_validation_rules.get("check_fields_format", True),
            required_check=address_validation_rules.get("check_required_fields", True),
            enable_normalization=address_validation_rules.get(
                "enable_fields_normalization", True
            ),
        )
        with traced_atomic_transaction():
            billing_address.save()
            change_billing_address_in_checkout(checkout, billing_address)
            info.context.plugins.checkout_updated(checkout)
        return CheckoutBillingAddressUpdate(checkout=checkout)
