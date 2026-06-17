{% snapshot snapshot_products %}

{{
    config(
        target_schema='snapshots',
        unique_key='product_id',

        strategy='check',
        check_cols=['row_hash'],

        invalidate_hard_deletes=True
    )
}}

SELECT *
FROM {{ ref('stg_products') }}

{% endsnapshot %}
