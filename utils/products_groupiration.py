import random
from collections import defaultdict, deque
from apps.product.models import Product

def get_product_group_id(product):
    return product.variant_group_id or product.id


def mix_products_by_groups(products, seed=None):
    rng = random.Random(seed)

    groups = defaultdict(list)

    for product in products:
        group_id = get_product_group_id(product)
        groups[group_id].append(product)

    group_queues = []

    for group_id, items in groups.items():
        rng.shuffle(items)

        group_queues.append({
            "group_id": group_id,
            "items": deque(items),
        })

    rng.shuffle(group_queues)

    result = []
    last_group_id = None

    while group_queues:
        available_groups = [
            group for group in group_queues
            if group["group_id"] != last_group_id
        ]

        if not available_groups:
            available_groups = group_queues

        group = rng.choice(available_groups)

        result.append(group["items"].popleft())
        last_group_id = group["group_id"]

        if not group["items"]:
            group_queues.remove(group)

    return result



def split_by_gender(products, selected_gender, page_size=30):
    if selected_gender not in ["male", "female"]:
        return products

    main_gender_products = [
        product for product in products
        if product.gender == selected_gender
    ]

    unisex_products = [
        product for product in products
        if product.gender == Product.Gender.UNISEX
    ]

    main_limit = round(page_size * 0.7)
    unisex_limit = page_size - main_limit

    selected = main_gender_products[:main_limit] + unisex_products[:unisex_limit]

    if len(selected) < page_size:
        used_ids = {product.id for product in selected}

        remaining = [
            product for product in products
            if product.id not in used_ids
        ]

        selected += remaining[:page_size - len(selected)]

    return selected